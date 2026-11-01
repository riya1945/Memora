from datetime import datetime, timezone
from uuid import UUID, uuid4

from memora.database import get_supabase_client
from memora.memory.models import Memory

LOCAL_OWNER_ID = UUID("00000000-0000-0000-0000-000000000001")


class MemoryStore:
    def __init__(self, use_supabase: bool = False):
        self.use_supabase = use_supabase
        self.memory: list[Memory] = []
        if use_supabase:
            self.client = get_supabase_client()
            self.owner_id = UUID(self.client.auth.get_user().user.id)
        else:
            self.client = None
            self.owner_id = LOCAL_OWNER_ID

    def save_memory(
        self,
        content: str,
        importance: float,
        confidence: float,
        embedding:list[float] | None= None,
        owner_id: UUID | None = None,
        project_id: UUID | None = None,
    ) -> Memory:
        now = datetime.now(timezone.utc)

        if owner_id is None:
            owner_id=self.owner_id
        
        if self.use_supabase:
            payload = {
                "content": content,
                "importance": importance,
                "confidence": confidence,
                "status": "active",
                
            }
            
            payload["owner_id"] = str(self.owner_id)    

            
            if project_id is not None:
                payload["project_id"] = str(project_id)
            if embedding is not None:
                payload["embedding"]=str(embedding)    
            response = (
                self.client.table("memories")
                .insert(payload)
                .execute()
            )

            if not response.data:
                raise RuntimeError(
                    "Supabase did not return the saved memory."
                )

            return Memory(**response.data[0])

        

        new_memory = Memory(
            id=uuid4(),
            owner_id=owner_id,
            project_id=project_id,
            content=content,
            created_at=now,
            updated_at=now,
            status="active",
            importance=importance,
            confidence=confidence,
        )

        self.memory.append(new_memory)
        return new_memory

    def get_memory(self, memory_id: UUID | str) -> Memory | None:
        memory_id = UUID(str(memory_id))

        if self.use_supabase:
            response = (
                self.client.table("memories")
                .select("*")
                .eq("id", str(memory_id))
                .limit(1)
                .execute()
            )

            return (
                Memory(**response.data[0])
                if response.data
                else None
            )

        return next(
            (
                memory
                for memory in self.memory
                if memory.id == memory_id
            ),
            None,
        )

    def list_memories(
        self,
        status: str | None = None,
    ) -> list[Memory]:
        if self.use_supabase:
            query = self.client.table("memories").select("*")

            if status is not None:
                query = query.eq("status", status)

            response = query.execute()
            return [Memory(**row) for row in response.data]

        memories = self.memory

        if status is not None:
            memories = [
                memory
                for memory in memories
                if memory.status == status
            ]

        return memories

    def archive_memory(
        self,
        memory_id: UUID | str,
    ) -> Memory | None:
        memory = self.get_memory(memory_id)

        if memory is None:
            return None

        if self.use_supabase:
            response = (
                self.client.table("memories")
                .update({
                    "status": "archived",
                    "updated_at": datetime.now(
                        timezone.utc
                    ).isoformat(),
                })
                .eq("id", str(memory.id))
                .execute()
            )

            return (
                Memory(**response.data[0])
                if response.data
                else None
            )

        memory.status = "archived"
        memory.updated_at = datetime.now(timezone.utc)
        return memory

    def update_memory(
        self,
        old_memory_id: UUID | str,
        new_memory_id: UUID | str,
    ):
        old_memory = self.get_memory(old_memory_id)
        new_memory = self.get_memory(new_memory_id)

        if old_memory is None or new_memory is None:
            return None

        if old_memory.id == new_memory.id:
            raise ValueError(
                "Old and new memory IDs must be different."
            )

        if old_memory.owner_id != new_memory.owner_id:
            raise ValueError(
                "Both memories must belong to the same owner."
            )

        if self.use_supabase:
            self.client.rpc(
                "replace_memory",
                {
                    "p_old_memory_id": str(old_memory.id),
                    "p_new_memory_id": str(new_memory.id),
                    "p_owner_id": str(old_memory.owner_id),
                },
            ).execute()

            now = datetime.now(timezone.utc)
            old_memory.status = "archived"
            old_memory.updated_at = now
            new_memory.status = "active"
            new_memory.updated_at = now

        else:
            now = datetime.now(timezone.utc)
            old_memory.status = "archived"
            new_memory.status = "active"
            old_memory.updated_at = now
            new_memory.updated_at = now

        return {
            "old_mem": old_memory,
            "new_mem": new_memory,
            "status": "updated",
        }
