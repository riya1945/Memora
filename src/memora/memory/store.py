from datetime import datetime, timezone
from uuid import UUID, uuid4
from pathlib import Path
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
        category: str | None=None,
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
            if category is not None:
                payload["category"] = category     
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
            category=category
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
    
    def list_categories(self)->list[str]:
            if self.use_supabase:
                response= self.client.table("memories").select("category").eq("status","active").execute()
                values=[row["category"] for row in response.data]

            else:
                values=[memory.category for memory in self.memory if memory.status=="active"]

            return sorted({v for v in values if v is not None})    

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
#Look for a project with the same name and owner_id.
#If it exists, update its root_path.
#If it doesn't exist, insert a new project with name, root_path, and owner_id.
#Return the project's UUID in either case.

    def get_or_create_project(self, name: str,root_path:str) -> UUID:
        if not self.use_supabase:
            raise NotImplementedError("Projects need Supabase mode.")

      
        check=self.client.table("projects").select("id").eq("name",name).eq("owner_id",str(self.owner_id)).limit(1).execute()
        root_path=str(Path(root_path).resolve())
        if check.data:
            self.client.table("projects").update({
    "root_path": root_path
}).eq("name", name).eq("owner_id", str(self.owner_id)).execute()
            return UUID(check.data[0]["id"])
            
        else:
            data=self.client.table("projects").insert({"name":name,"root_path":root_path,"owner_id":str(self.owner_id)}).execute()
            return UUID(data.data[0]["id"])
    
    def list_projects(self):
        if not self.use_supabase:
            return []
        response=self.client.table("projects").select("id","name","root_path").eq("owner_id",str(self.owner_id)).execute()
        return response.data
    
    def get_project(self,project_id:UUID):
        response=self.client.table("projects").select("id","name","root_path").eq("id",project_id).eq("owner_id",self.owner_id).execute()
        if not response.data:
            return None
        else:
            return response.data[0] 

    def save_edit_proposal(
    self,
    project_id: UUID | str,
    user_path: str,
    original_hash: str,
    new_content: str,
    diff: str,
):
        if not self.use_supabase:
            raise NotImplementedError(
            "Edit proposals need Supabase mode."
        )

        payload = {
        "owner_id": str(self.owner_id),
"project_id": str(project_id),"user_path":user_path,"original_hash":original_hash,"new_content":new_content,"diff":diff
    }

        response = (
        self.client.table("edit_proposals").insert(payload).execute()
    )

        if not response.data:
            raise RuntimeError("Proposal was not saved.")

        return response.data[0]    
    def get_edit_proposal(self, proposal_id: UUID | str):
        if not self.use_supabase:
            raise NotImplementedError(
            "Edit proposals need Supabase mode."
        )

        response = (
        self.client.table("edit_proposals")
        .select("*")
        .eq("id", str(proposal_id)).eq("owner_id", str(self.owner_id))
        .execute()
    )

        if not response.data:
            return None

        return response.data[0]   
    def update_edit_proposal_status(
    self,
    proposal_id: UUID | str,
    status: str,
):
        if not self.use_supabase:
            raise NotImplementedError(
            "Edit proposals need Supabase mode."
        )

        allowed_statuses = {"rejected", "applied", "failed"}

    
        if status not in allowed_statuses:
            raise ValueError("Invalid proposal status.")

    
        payload = {"status": status}

        if status == "applied":
            payload["applied_at"] = datetime.now(
            timezone.utc
        ).isoformat()

    
        response = (
        self.client.table("edit_proposals")
        .update(payload)
        .eq("id", str(proposal_id))
        .eq("owner_id", str(self.owner_id))
        .eq("status", "pending")
        .select("*")
        .execute()
    )

    
        if not response.data:
            return None

        return response.data[0]

    def get_project_root(self, project_id: UUID | str) -> str | None:
        if not self.use_supabase:
            return None

        response = (
        self.client.table("projects")
        .select("root_path")
        .eq("id", str(project_id))
        .limit(1)
        .execute()
    )
        if not response.data:
            return None

        return response.data[0].get("root_path")
    def list_pending_proposals(
    self,
    project_id: UUID | str,
    created_after: datetime | None = None
):
        if not self.use_supabase:
            raise NotImplementedError("Edit proposals need Supabase mode.")

        query = (
        self.client.table("edit_proposals")
        .select("*")
        .eq("project_id", str(project_id))
        .eq("owner_id", str(self.owner_id))
        .eq("status", "pending")
    )

        if created_after:
            query = query.gte("created_at", created_after.isoformat())

        response = query.order("created_at").execute()

        return response.data or []