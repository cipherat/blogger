import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from typing import Any, Tuple, Optional, List, Dict


class PostgresClient:
    def __init__(self, dbname, user, password, host, port, min_conn=1, max_conn=10):
        try:
            self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
                min_conn,
                max_conn,
                dbname=dbname,
                user=user,
                password=password,
                host=host,
                port=port,
                cursor_factory=RealDictCursor,
            )
        except Exception as e:
            print(f"Error creating connection pool: {e}")
            raise

    def call_function(self, function_name: str, params: Tuple = (), commit: bool = False) -> Optional[List[Dict[str, Any]]]:
        conn = None
        try:
            conn = self.connection_pool.getconn()
            with conn.cursor() as cur:
                cur.callproc(function_name, params)
                
                result = None
                if cur.description:
                    result = cur.fetchall()
                
                if commit:
                    conn.commit()
                
                return result
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Database error during {function_name}: {e}")
            raise
        finally:
            if conn:
                self.connection_pool.putconn(conn)

    def close_all(self):
        if self.connection_pool:
            self.connection_pool.closeall()
