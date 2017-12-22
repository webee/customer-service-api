test_customers_data = [
    {"uid": "test", "name": "测试客户", "mobile": "18812345678"},
    {"uid": "test_001", "name": "测试客户#1", "mobile": "15912345678"},
    {"uid": "test_002", "name": "", "mobile": "12387654321"},
    {"uid": "test_003", "name": "测试客户#3"}
]

test_staff_label_tree = {
    "1": {"name": "角色#1", "children": [
        {"code": "1", "name": "分组#1"},
        {"code": "2", "name": "分组#2"}
    ]},
    "2": {"name": "角色#2", "children": {
        "1": {"name": "分组#1"}
    }},
}

test_staffs_data = [
    {"uid": "test", "name": "测试客服",
     "context_labels": [{"type": "self", "path": "1.1"}, {"type": "sub", "path": "2.1"}, ]},
    {"uid": "test_x", "name": "测试客服#x",
     "context_labels": [["self", ""], ]},
    {"uid": "test_01", "name": "测试客服#1",
     "context_labels": [["sub", "1.1"], ]},
    {"uid": "test_02", "name": "测试客服#2",
     "context_labels": [["self", "2.1"], ]},
    {"uid": "test_03", "name": "测试客服#3",
     "context_labels": [["self", "1.2"], ]},
    {"uid": "test_04", "name": "测试客服#4",
     "context_labels": [["sub", "1.2"], ]},
    {"uid": "test_05", "name": "测试客服#5",
     "context_labels": [["sub", "1.2"], ]},
]

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
        "scope_labels": [
            {"type": "all", "path": "1.1"},
            ["self", "1.2"]
        ],
        "meta_data": [
            {"value": "测试用户", "label": "姓名"},
            {"value": 28, "label": "年龄"},
            {"type": "link", "value": {"value": "详情", "href": "https://www.baidu.com/"}, "label": "用户详情"},
            ["测试x", "value", "xxxxx"]
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
        "tags": ['测试类型2'],
        "scope_labels": [
            {"type": "all", "path": "1.1"},
            ["self", "1.2"]
        ],
        "meta_data": [
            {"value": "用户002", "label": "姓名"},
            {"value": True, "label": "是否有效"},
            {"type": "link", "value": {"value": "详情", "href": "https://www.baidu.com/"}, "label": "用户详情"},
            ["测试y", "value", "yyyyy"]
        ]
    },
    {
        "domain": "test",
        "type": "test",
        "biz_id": "t_0003",
        "start_msg_id": 0,
        "owner": {
            "uid": "test",
        },
        "leader": {
            "uid": "test"
        },
        "customers": [
            {
                "uid": "test",
            }
        ],
        "tags": ['超长的测试类型x'],
        "scope_labels": [
            ["self", "1.2:test"]
        ],
        "meta_data": [
            {"value": "用户002", "label": "姓名"},
            {"value": True, "label": "是否有效"},
            {"type": "link", "value": {"value": "详情", "href": "https://www.baidu.com/"}, "label": "用户详情"},
            ["测试y", "value", "yyyyy"]
        ]
    }
]
