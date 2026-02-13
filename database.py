import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL")

engine = create_engine(DATABASE_URL) if DATABASE_URL else None
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) if engine else None
Base = declarative_base()


class VideoModel(Base):
    __tablename__ = "videos"
    
    id = Column(String(36), primary_key=True)
    filename = Column(String(255), nullable=False)
    original_name = Column(String(255), nullable=False)
    size = Column(Integer, nullable=False)
    duration = Column(Float, nullable=False)
    path = Column(String(500), nullable=False)
    codec = Column(String(50), nullable=True)
    resolution = Column(String(20), nullable=True)
    bitrate = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_temporary = Column(Boolean, default=False)


class JobModel(Base):
    __tablename__ = "jobs"
    
    id = Column(String(36), primary_key=True)
    type = Column(String(20), nullable=False)  # 'split' or 'merge'
    status = Column(String(20), nullable=False, default='pending')
    progress = Column(Integer, default=0)
    video_id = Column(String(36), nullable=True)
    video_ids = Column(Text, nullable=True)  # JSON array for merge
    segment_duration = Column(Integer, nullable=True)
    outputs = Column(Text, nullable=True)  # JSON array
    output = Column(String(255), nullable=True)
    error = Column(Text, nullable=True)
    convert_720 = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class TikTokDownloadModel(Base):
    __tablename__ = "tiktok_downloads"
    
    id = Column(String(36), primary_key=True)
    url = Column(String(500), nullable=False)
    filename = Column(String(255), nullable=False)
    title = Column(Text, nullable=True)
    uploader = Column(String(255), nullable=True)
    duration = Column(Float, nullable=True)
    view_count = Column(Integer, nullable=True)
    like_count = Column(Integer, nullable=True)
    path = Column(String(500), nullable=False)
    platform = Column(String(50), nullable=True)
    media_type = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_downloaded = Column(Boolean, default=False)


class StatsModel(Base):
    __tablename__ = "stats"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    total_videos_split = Column(Integer, default=0)
    total_segments_created = Column(Integer, default=0)
    total_videos_merged = Column(Integer, default=0)
    total_time_saved = Column(Float, default=0)
    total_tiktok_downloads = Column(Integer, default=0)


def get_db():
    if SessionLocal is None:
        return None
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    if engine is None:
        print("No DATABASE_URL configured")
        return False
    
    try:
        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        
        # Check for missing columns (Migration Logic)
        from sqlalchemy import inspect, text
        inspector = inspect(engine)

        for table_name, table in Base.metadata.tables.items():
            if inspector.has_table(table_name):
                existing_columns = [c['name'] for c in inspector.get_columns(table_name)]
                for column in table.columns:
                    if column.name not in existing_columns:
                        print(f"Migrating: Adding missing column '{column.name}' to table '{table_name}'")
                        try:
                            # Compile the column type for the specific dialect (PostgreSQL or SQLite)
                            col_type = column.type.compile(engine.dialect)

                            # Construct ALTER TABLE statement
                            # Note: We rely on the database to handle defaults/nullability if possible,
                            # but purely adding the column is the primary goal.
                            # For SQLite and Postgres, basic ADD COLUMN works.
                            # We wrap names in quotes to handle reserved words or case sensitivity
                            sql = f'ALTER TABLE "{table_name}" ADD COLUMN "{column.name}" {col_type}'

                            # Add server default if specified (basic support)
                            if column.server_default is not None:
                                # This is complex to extract string representation reliably, skipping for safety
                                pass

                            with engine.connect() as conn:
                                conn.execute(text(sql))
                                conn.commit()
                                print(f"Successfully added column '{column.name}' to '{table_name}'")
                        except Exception as e:
                            print(f"Error adding column '{column.name}' to '{table_name}': {e}")

        db = SessionLocal()
        stats = db.query(StatsModel).first()
        if not stats:
            stats = StatsModel(
                total_videos_split=0,
                total_segments_created=0,
                total_videos_merged=0,
                total_time_saved=0,
                total_tiktok_downloads=0
            )
            db.add(stats)
            db.commit()
        db.close()
        
        print("Database initialized successfully!")
        return True
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False


def cleanup_all():
    """Clean up all data from database tables (except stats) and return True if successful."""
    if SessionLocal is None:
        return False
    
    try:
        db = SessionLocal()
        db.query(VideoModel).delete()
        db.query(JobModel).delete()
        db.query(TikTokDownloadModel).delete()
        db.commit()
        db.close()
        return True
    except Exception as e:
        print(f"Error cleaning up database: {e}")
        return False


if __name__ == "__main__":
    init_db()
