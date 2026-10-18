# -*- coding: utf-8 -*-
"""
重置第三届学生干部的登录密码为 123456
用法: cd /opt/material-system && /opt/material-system/venv/bin/python reset_passwords.py
"""
import sqlite3
import bcrypt
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, 'data', 'material.db')


def main():
    if not os.path.exists(DB):
        print(f"[错误] 数据库不存在: {DB}")
        sys.exit(1)
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    new_hash = bcrypt.hashpw(b"123456", bcrypt.gensalt()).decode("utf-8")
    cur.execute(
        "UPDATE users SET password_hash=? WHERE cohort=?",
        (new_hash, "第三届"),
    )
    count = cur.rowcount
    conn.commit()
    print(f"已重置 {count} 名第三届用户的密码为 123456")
    # 验证
    r = cur.execute(
        "SELECT username, real_name FROM users WHERE cohort=? ORDER BY real_name",
        ("第三届",),
    ).fetchall()
    for row in r:
        print(f"  {row[1]} ({row[0]})")
    conn.close()


if __name__ == "__main__":
    main()
