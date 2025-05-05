from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import openai
import json

router = APIRouter()

class ChatRequest:
    message: str
    conversation_id: str = None

@router.post("/chat")
async def chat_stream(request: ChatRequest):
    try:
        # Get agent config (versioned)
        config = get_agent_config(request.conversation_id)
        
        # Stream tokens from OpenAI
        response = await openai.ChatCompletion.acreate(
            model=config.model,
            messages=[{"role": "user", "content": request.message}],
            stream=True,
            tools=tool_configurations()  # See section 2
        )
        
        async def generate():
            full_response = ""
            async for chunk in response:
                token = chunk.choices[0].delta.get("content", "")
                if token:
                    full_response += token
                    yield token
                
                # Handle tool calls (actions)
                if tool_calls := chunk.choices[0].delta.get("tool_calls"):
                    yield from handle_actions(tool_calls)
            
            save_conversation(request.conversation_id, full_response)

        return StreamingResponse(generate(), media_type="text/event-stream")

    except Exception as e:
        raise HTTPException(500, str(e))