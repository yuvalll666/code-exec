# init_db.py
from shared.db.database import Base, engine
from shared.db.models import CodeJob

print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Done!")