# EatLose 日记接入示例

用一个 Python 示例统计一周确认了几餐，以及有蛋白质估算值的日子里，平均每天记录了多少克。虚构示例和用户授权的日记使用同一个计算函数。[English](README.md)

## 先用虚构日记试一次

在仓库根目录运行以下命令。只需 Python 3，示例数据已随仓库附上，可以离线运行。

```sh
python3 examples/weekly_recap.py
```

示例有 **6 天记了餐，共 14 餐**。这 6 天的餐食都有蛋白质估算值，平均每天记录了 **71.3 克**。程序输出 JSON，可以直接交给自己的工具或助手。想在聊天框里试同一份数据，可以从官网复制完整提问。[试做饮食周报](https://eatlose.com/zh/agents/#try)

也可以直接获取公开的虚构数据。

```sh
curl -fsS https://eatlose.com/agents/sample-week.json
```

## 接入自己授权的日记

1. 在 EatLose 打开 **「我的 → 连接 Agent」**。选择是否包含自己记录的体重，点 **「授权并复制指令」**。
2. 运行 `python3 examples/weekly_recap.py --live`。出现隐藏输入提示时，只粘贴指令中 `Bearer` 后面那段令牌。程序向 EatLose 读取一次摘要，在本地输出周报。
3. 在 **「连接 Agent → 断开连接」** 可随时撤权。授权最长 30 天，生成新指令会立即替换旧指令。

服务端集成可以从自己的密钥存储把令牌注入环境变量 `EATLOSE_DIARY_TOKEN`，每个用户单独保存。公开的仓库、示例、Issue 和日志都使用虚构数据，真实令牌和日记只在授权范围内使用。

## 在自己的代码里调用

使用只读 GET 请求，把令牌放在 HTTP 请求头。以下命令使用本地已设置的 `EATLOSE_DIARY_TOKEN`。

```sh
curl -fsS -H "Authorization: Bearer ${EATLOSE_DIARY_TOKEN:?Set the diary token first}" \
  https://kgnnsvcrxefvavdyvakk.supabase.co/functions/v1/agent-diary
```

- 接口按日记时区返回含今天在内的 7 个日期。每行统计当天已确认、已同步的餐食。缺少某个日期表示当天没有这样的记录，有记录的日子也可能只记了部分餐食。
- 热量和营养素都是**估算值**。某项营养素为 `null` 表示当天至少一餐缺少这项估算，计算平均值时应保留未知含义。数值 0 是已知值。
- `last_reported_device_sync_at` 是设备最近一次报告同步成功的时间，可能为空。`cloud_read_at` 是服务端读取摘要的时间。
- 用户勾选分享体重后，响应才包含 `user_logged_weights`。Apple 健康和 Health Connect 的设备记录不在这项授权范围内。
- `401 invalid_connection` 表示需要用户检查授权，`503 unavailable` 可以稍后重试。该接口只接受 GET，其他方法会返回 405。

请求和响应字段见 [OpenAPI 接口说明](openapi.json)。[虚构响应样本](examples/sample-week.json)包含一天没有记餐，以及一天缺少脂肪估算值的情况。

## 运行测试

```sh
python3 -m unittest discover -s tests
```
