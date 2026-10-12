# -*- coding: utf-8 -*-
"""
导入第三届学生干部通讯录到用户系统
- 以"姓名"为用户名，届别=第三届，默认密码 123456，角色=普通用户，状态=已通过
- 用户名或真实姓名已存在时跳过（不重复创建）
- 用法: cd /opt/material-system && /opt/material-system/venv/bin/python import_third_cohort.py
"""
import sqlite3
import uuid
import bcrypt
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, 'data', 'material.db')

# (姓名, 部门, 电话, 届别)
# 数据来源：重庆超大城市数字化治理学院第三届团总支学生会学生干部通讯录
PEOPLE = [
    ("周新越", "副书记", "18623527845", "第三届"),
    ("杨光月", "主席团", "17341595385", "第三届"),
    ("朱涛", "主席团", "18983831636", "第三届"),
    ("李玉清", "主席团", "19054095280", "第三届"),
    ("张诗涵", "主席团", "13386627740", "第三届"),
    ("钱俊雨", "主席团", "18795565064", "第三届"),
    ("向卓越", "组织部", "15730621577", "第三届"),
    ("雷斯媛", "组织部", "18696517967", "第三届"),
    ("张彦华", "组织部", "17726237767", "第三届"),
    ("黄玉辉", "权益部", "19115224287", "第三届"),
    ("陈娅轩", "权益部", "17783470869", "第三届"),
    ("陈沿竹", "社团部", "19923312909", "第三届"),
    ("徐晓宝", "社团部", "19292469698", "第三届"),
    ("刘语欣", "宣传部", "18580003307", "第三届"),
    ("王小漫", "宣传部", "17264213002", "第三届"),
    ("伍悦", "宣传部", "19502354606", "第三届"),
    ("刘秋玲", "办公室", "17358302529", "第三届"),
    ("姜涵焫", "办公室", "19115289353", "第三届"),
    ("刘辰辰", "办公室", "19132822615", "第三届"),
    ("岳文霞", "体育部", "19908327048", "第三届"),
    ("冉儒举", "体育部", "17815156636", "第三届"),
    ("吴泽慷", "体育部", "19823829538", "第三届"),
    ("任佳乐", "文娱部", "19115573500", "第三届"),
    ("薛海鹏", "文娱部", "17784207760", "第三届"),
    ("周月秀", "马列部", "19823321393", "第三届"),
    ("孙璇", "马列部", "19823582082", "第三届"),
    ("盛雯丽", "学习部", "17323950017", "第三届"),
    ("但渝锦", "学习部", "19562111704", "第三届"),
    ("叶佳男", "志工部", "13957273801", "第三届"),
    ("熊颖", "志工部", "17708304578", "第三届"),
]


def main():
    if not os.path.exists(DB):
        print(f"[错误] 数据库不存在: {DB}")
        sys.exit(1)
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # 确保第三届届别存在
    cur.execute("SELECT id FROM cohorts WHERE name=?", ("第三届",))
    if not cur.fetchone():
        cur.execute("INSERT INTO cohorts (id, name, sort_order) VALUES (?, ?, ?)",
                    (str(uuid.uuid4()), "第三届", 1))
        print("[提示] 已创建届别：第三届")

    imported, skipped = 0, []
    for name, dept, phone, cohort in PEOPLE:
        # 重复检查：用户名 或 真实姓名 已存在则跳过
        cur.execute("SELECT id, username FROM users WHERE username=? OR real_name=?",
                    (name, name))
        if cur.fetchone():
            skipped.append(name)
            continue
        uid = str(uuid.uuid4())
        ph = bcrypt.hashpw(b"123456", bcrypt.gensalt()).decode()
        cur.execute(
            """INSERT INTO users
               (id, username, password_hash, real_name, phone, email,
                department, cohort, role, status, created_at)
               VALUES (?,?,?,?,?,?,?,?, 'user', 'approved', datetime('now','localtime'))""",
            (uid, name, ph, name, phone, "", dept, cohort),
        )
        imported += 1

    conn.commit()
    print("=" * 48)
    print("导入完成！")
    print(f"  成功导入: {imported} 人")
    print(f"  跳过(已存在): {len(skipped)} 人 -> {skipped}")
    print("=" * 48)
    print("默认登录密码: 123456  （登录后可在个人设置修改）")
    print("提示：这些成员已在系统用户管理中，可重置密码/禁用/删除")
    conn.close()


if __name__ == "__main__":
    main()
