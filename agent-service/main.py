# main.py
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import openai
import redis
import json
import os
from azure.servicebus import ServiceBusClient, ServiceBusMessage

app = FastAPI()

# Configuration
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
SERVICE_BUS_CONN_STR = os.getenv("SERVICE_BUS_CONN_STR")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize clients
redis_client = redis.StrictRedis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    ssl=True,
    decode_responses=True
)
openai.api_key = OPENAI_API_KEY
servicebus_client = ServiceBusClient.from_connection_string(SERVICE_BUS_CONN_STR)

# Auth
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Validate token with AAD
    # Implementation depends on your AAD setup
    return {"user_id": "user123"}  # Simplified for example

class ChatRequest(BaseModel):
    message: str
    agent_id: str
    conversation_id: str = None

class AgentAction(BaseModel):
    action_type: str
    parameters: dict

@app.post("/chat")
async def chat_stream(
    request: ChatRequest,
    user: dict = Depends(get_current_user),
    raw_request: Request
):
    # Get agent configuration
    agent_config = get_agent_config(request.agent_id)
    
    # Check cache for conversation history
    conversation_key = f"conversation:{request.conversation_id or 'new'}"
    history = redis_client.get(conversation_key) or "[]"
    messages = json.loads(history)
    
    # Add new message
    messages.append({"role": "user", "content": request.message})
    
    # Call OpenAI with streaming
    response = openai.ChatCompletion.create(
        model=agent_config["model"],
        messages=messages,
        stream=True,
        tools=[{
            "type": "function",
            "function": {
                "name": "change_notification_settings",
                "description": "Change user notification settings",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "email_notifications": {"type": "boolean"},
                        "push_notifications": {"type": "boolean"}
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "change_theme",
                "description": "Change application theme",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "theme": {"type": "string", "enum": ["light", "dark"]}
                    }
                }
            }
        }]
    )
    
    # Stream response
    async def generate():
        full_response = ""
        for chunk in response:
            delta = chunk.choices[0].delta
            if delta.content:
                token = delta.content
                full_response += token
                yield token
            elif delta.tool_calls:
                # Handle tool calls (actions)
                for tool_call in delta.tool_calls:
                    action = AgentAction(
                        action_type=tool_call.function.name,
                        parameters=json.loads(tool_call.function.arguments)
                    
                    # Send to Service Bus for processing
                    sender = servicebus_client.get_queue_sender("actions")
                    message = ServiceBusMessage(
                        body=json.dumps({
                            "user_id": user["user_id"],
                            "action": action.dict(),
                            "conversation_id": request.conversation_id
                        })
                    )
                    await sender.send_messages(message)
        
        # Update conversation history
        messages.append({"role": "assistant", "content": full_response})
        redis_client.set(conversation_key, json.dumps(messages), ex=3600)
    
    return StreamingResponse(generate(), media_type="text/event-stream")

def get_agent_config(agent_id: str):
    # Implementation would fetch from Azure Blob Storage
    # This is a simplified version
    return {
        "model": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 1000,
        "version": "1.0.0"
    }