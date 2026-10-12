# -*- coding: utf-8 -*-
"""
导入/更新第三届学生干部通讯录（v2：修正数据 + 拼音用户名）
- 用户名 = 姓名全拼小写（如 周新越 -> zhouxinyue）
- 按 real_name 匹配：已存在的用户 -> 更新 用户名/部门/电话/届别（资料修正）；不存在的 -> 新建
- 默认密码 123456（仅新建时生效）
- 用法: cd /opt/material-system && /opt/material-system/venv/bin/python import_third_cohort.py
"""
import sqlite3
import uuid
import bcrypt
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, 'data', 'material.db')

# (拼音用户名, 姓名, 部门, 电话, 届别)
# 数据来源：重庆超大城市数字化治理学院第三届团总支学生会学生干部通讯录（修正版）
PEOPLE = [
    ("zhouxinyue", "周新越", "副书记", "18623527845", "第三届"),
    ("yangguangyue", "杨光月", "副书记", "17341595385", "第三届"),
    ("zhutao", "朱涛", "主席团", "18983831636", "第三届"),
    ("liyuqing", "李玉清", "主席团", "19054095280", "第三届"),
    ("zhangshihan", "张诗涵", "主席团", "13386627740", "第三届"),
    ("qianjunyu", "钱俊雨", "主席团", "18795565064", "第三届"),
    ("xiangzhuoyue", "向卓越", "组织部", "15730621577", "第三届"),
    ("leisiyuan", "雷斯媛", "组织部", "18696517967", "第三届"),
    ("zhangyanhua", "张彦华", "组织部", "17726237767", "第三届"),
    ("huangyuhui", "黄玉辉", "权益部", "19115242837", "第三届"),
    ("chenyaxuan", "陈娅轩", "权益部", "17783470869", "第三届"),
    ("chenyanzhu", "陈沿竹", "社团部", "19923312909", "第三届"),
    ("xuxiaobao", "徐晓宝", "社团部", "19292469698", "第三届"),
    ("liuyuxin", "刘语欣", "宣传部", "18580003307", "第三届"),
    ("wangxiaoman", "王小漫", "宣传部", "17264213002", "第三届"),
    ("wuyue", "伍悦", "宣传部", "19502354606", "第三届"),
    ("liuqiuling", "刘秋玲", "办公室", "17358302529", "第三届"),
    ("jianghankun", "姜涵焜", "办公室", "19115289353", "第三届"),
    ("liuzhanchen", "刘展辰", "办公室", "19132822615", "第三届"),
    ("yuewenxia", "岳文霞", "体育部", "19908327048", "第三届"),
    ("ranruju", "冉儒举", "体育部", "17815156636", "第三届"),
    ("wuzekang", "吴泽慷", "文娱部", "19823829538", "第三届"),
    ("renjiale", "任佳乐", "文娱部", "19115573500", "第三届"),
    ("xuehaipeng", "薛海鹏", "文娱部", "17784207760", "第三届"),
    ("zhouyuexiu", "周月秀", "马列部", "19823321393", "第三届"),
    ("sunxuan", "孙璇", "马列部", "19823582082", "第三届"),
    ("shengwenli", "盛雯丽", "学习部", "17323950017", "第三届"),
    ("danyujin", "但渝锦", "学习部", "19562111704", "第三届"),
    ("yejianan", "叶佳男", "志工部", "13957273801", "第三届"),
    ("xiongying", "熊颖", "志工部", "17708304578", "第三届"),
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

    created, updated, skipped = [], [], []
    for uname, name, dept, phone, cohort in PEOPLE:
        # 按真实姓名匹配
        cur.execute("SELECT id, username FROM users WHERE real_name=?", (name,))
        row = cur.fetchone()
        if row:
            uid, old_uname = row[0], row[1]
            # 用户名被其他用户占用时跳过改名
            cur.execute("SELECT id FROM users WHERE username=? AND id<>?", (uname, uid))
            if cur.fetchone():
                skipped.append(f"{name}（拼音用户名 {uname} 已被占用）")
                continue
            cur.execute(
                "UPDATE users SET username=?, phone=?, department=?, cohort=? WHERE id=?",
                (uname, phone, dept, cohort, uid),
            )
            updated.append(f"{name}（{old_uname} -> {uname}）")
        else:
            uid = str(uuid.uuid4())
            ph = bcrypt.hashpw(b"123456", bcrypt.gensalt()).decode()
            cur.execute(
                """INSERT INTO users
                   (id, username, password_hash, real_name, phone, email,
                    department, cohort, role, status, created_at)
                   VALUES (?,?,?,?,?,?,?,?, 'user', 'approved', datetime('now','localtime'))""",
                (uid, uname, ph, name, phone, "", dept, cohort),
            )
            created.append(name)

    conn.commit()
    print("=" * 48)
    print("执行完成！")
    print(f"  新建用户: {len(created)} 人 -> {created}")
    print(f"  更新资料: {len(updated)} 人 ->")
    for u in updated:
        print(f"    - {u}")
    if skipped:
        print(f"  跳过: {len(skipped)} 人 -> {skipped}")
    print("=" * 48)
    print("默认登录密码(仅新建): 123456")
    conn.close()


if __name__ == "__main__":
    main()
