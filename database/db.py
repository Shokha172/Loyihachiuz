import aiosqlite
from config import DB_NAME, SUPER_ADMIN_ID, ADMIN_IDS

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        # admins table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                tg_id INTEGER PRIMARY KEY
            )
        """)
        # users table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                tg_id INTEGER PRIMARY KEY,
                full_name TEXT,
                address TEXT,
                phone TEXT,
                loyiha_toifasi TEXT DEFAULT 'Kiritilmagan',
                service_type TEXT DEFAULT 'Kiritilmagan',
                stage TEXT DEFAULT 'Kiritilmagan',
                tur TEXT DEFAULT 'Kiritilmagan',
                eng_kam_ish_haqi TEXT DEFAULT '3 barobari',
                total_sum REAL DEFAULT 0.0,
                paid_sum REAL DEFAULT 0.0,
                payment_method TEXT DEFAULT 'Kiritilmagan',
                receipt_file_id TEXT,
                status TEXT DEFAULT 'Kutilmoqda',
                created_at TEXT
            )
        """)
        # Add all admins if not exists
        for admin_id in ADMIN_IDS:
            await db.execute("INSERT OR IGNORE INTO admins (tg_id) VALUES (?)", (admin_id,))
        await db.commit()

async def add_admin(tg_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT OR IGNORE INTO admins (tg_id) VALUES (?)", (tg_id,))
        await db.commit()

async def delete_admin(tg_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM admins WHERE tg_id = ?", (tg_id,))
        await db.commit()

async def is_admin(tg_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT 1 FROM admins WHERE tg_id = ?", (tg_id,)) as cursor:
            return await cursor.fetchone() is not None

async def add_user(tg_id, full_name, address, phone, created_at):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT OR REPLACE INTO users (tg_id, full_name, address, phone, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (tg_id, full_name, address, phone, created_at))
        await db.commit()

async def update_user_project(tg_id, data):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            UPDATE users SET 
                loyiha_toifasi = ?, 
                service_type = ?, 
                stage = ?, 
                tur = ?, 
                total_sum = ?, 
                paid_sum = ?,
                payment_method = ?,
                receipt_file_id = ?,
                status = 'Jarayonda'
            WHERE tg_id = ?
        """, (
            data.get('loyiha_toifasi'),
            data.get('service_type'),
            data.get('stage'),
            data.get('tur'),
            data.get('total_sum'),
            data.get('paid_sum'),
            data.get('payment_method'),
            data.get('receipt_file_id'),
            tg_id
        ))
        await db.commit()

async def get_user(tg_id):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE tg_id = ?", (tg_id,)) as cursor:
            return await cursor.fetchone()

async def update_user_status(tg_id, status):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE users SET status = ? WHERE tg_id = ?", (status, tg_id))
        await db.commit()

async def get_all_users():
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users ORDER BY created_at DESC") as cursor:
            return await cursor.fetchall()

async def get_pending_users():
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE status = 'Kutilmoqda' ORDER BY created_at DESC") as cursor:
            return await cursor.fetchall()

async def get_stats():
    async with aiosqlite.connect(DB_NAME) as db:
        query = """
            SELECT 
                COUNT(*) as total_users,
                SUM(total_sum) as total_contracts,
                SUM(paid_sum) as total_paid
            FROM users
        """
        async with db.execute(query) as cursor:
            row = await cursor.fetchone()
            return {
                "total_users": row[0],
                "total_contracts": row[1] or 0,
                "total_paid": row[2] or 0
            }
