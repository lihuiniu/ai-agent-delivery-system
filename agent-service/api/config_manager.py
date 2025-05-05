from pydantic import BaseModel
import yaml
from azure.storage.blob import BlobServiceClient

class AgentConfig(BaseModel):
    version: str
    model: str = "gpt-4"
    temperature: float = 0.7
    tools: list[str] = ["notifications", "theme_switch"]
    prompt_template: str

def get_agent_config(conversation_id: str) -> AgentConfig:
    blob_client = BlobServiceClient.from_connection_string(
        os.getenv("STORAGE_CONN_STR"))
    
    # Get latest config by default or versioned config for conversation
    blob_name = f"configs/{conversation_id}.yaml" if conversation_id else "configs/latest.yaml"
    
    stream = blob_client.get_blob_client(
        container="agent-configs",
        blob=blob_name).download_blob().readall()
    
    return AgentConfig(**yaml.safe_load(stream))