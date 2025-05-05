from azure.servicebus import ServiceBusClient
from pydantic import BaseModel

class ActionRequest(BaseModel):
    user_id: str
    action_type: str
    parameters: dict

def tool_configurations():
    return [
        {
            "type": "function",
            "function": {
                "name": "change_notification_settings",
                "description": "Update user notification preferences",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "email_enabled": {"type": "boolean"},
                        "push_enabled": {"type": "boolean"}
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "switch_theme",
                "description": "Change UI theme",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "theme": {"type": "string", "enum": ["light", "dark"]}
                    }
                }
            }
        }
    ]

async def handle_actions(tool_calls):
    sb_client = ServiceBusClient.from_connection_string(
        os.getenv("SERVICE_BUS_CONN_STR"))
    
    for tool in tool_calls:
        action = ActionRequest(
            user_id=get_current_user(),
            action_type=tool.function.name,
            parameters=json.loads(tool.function.arguments)
        
        async with sb_client.get_queue_sender("actions") as sender:
            await sender.send_messages(
                ServiceBusMessage(json.dumps(action.dict())))
        
        yield f"\n[ACTION: {action.action_type} queued]"