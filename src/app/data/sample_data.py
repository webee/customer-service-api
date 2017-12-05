test_projects_data = [
    {
        "domain": "test",
        "type": "test",
        "biz_id": "t_0001",
        "start_msg_id": 0,
        "owner": {
            "uid": "test",
            "name": "测试用户"
        },
        "leader": {
            "uid": "test",
            "name": "测试客服"
        },
        "customers": [
            {
                "uid": "test",
                "name": "测试用户"
            },
            {
                "uid": "u#001",
                "name": "用户001"
            }
        ],
        "meta_data": [
            {"key": "username", "value": "测试用户", "label": "姓名", "index": 1},
            {"key": "age", "value": 28, "label": "年龄", "index": 2},
            {"key": "user_details", "type": "link", "value": {"value": "详情", "href": "https://www.baidu.com/"},
             "label": "用户详情", "index": 3},
            {"key": "test_x", "type": "value", "value": "xxxxx", "label": "测试x", "index": 4}
        ]
    },
    {
        "domain": "test",
        "type": "test",
        "biz_id": "t_0002",
        "start_msg_id": 0,
        "owner": {
            "uid": "u#002",
            "name": "用户002"
        },
        "leader": {
            "uid": "test"
        },
        "customers": [
            {
                "uid": "u#002",
                "name": "用户002"
            }
        ],
        "meta_data": [
            {"key": "username", "value": "用户002", "label": "姓名", "index": 1},
            {"key": "is_valid", "value": True, "label": "是否有效", "index": 2},
            {"key": "user_details", "type": "link", "value": {"value": "详情", "href": "https://www.baidu.com/"},
             "label": "用户详情", "index": 3},
            {"key": "test_y", "type": "value", "value": "yyyyy", "label": "测试y", "index": 4}
        ]
    }
]
