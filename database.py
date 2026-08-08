import datetime

# 模擬訂單資料庫
ORDERS_DB = {
    "1001": {
        "order_id": "1001",
        "item": "Wireless Headphones",
        "status": "Delivered",
        "delivery_date": datetime.date.today() - datetime.timedelta(days=2),  # 2天前送達（符合 <=14天退款條件）
        "price": 120.0,
        "refunded": False
    },
    "1002": {
        "order_id": "1002",
        "item": "Smartwatch",
        "status": "In Transit",
        "delivery_date": None,
        "price": 250.0,
        "refunded": False
    }
}


def get_order_details(order_id: str):
    """根據訂單 ID 查詢訂單詳情"""
    order = ORDERS_DB.get(str(order_id))
    if not order:
        return {"error": f"Order #{order_id} not found."}

    return {
        "order_id": order["order_id"],
        "item": order["item"],
        "status": order["status"],
        "delivery_date": (
            str(order["delivery_date"]) if order["delivery_date"] else "N/A"
        ),
        "price": order["price"],
        "refunded": order["refunded"],
    }


def process_refund(order_id: str, reason: str):
    """處理訂單退款申請"""
    order = ORDERS_DB.get(str(order_id))
    if not order:
        return {"status": "failed", "reason": f"Order #{order_id} not found."}

    if order["refunded"]:
        return {
            "status": "failed",
            "reason": f"Order #{order_id} has already been refunded.",
        }

    if order["status"] != "Delivered":
        return {
            "status": "failed",
            "reason": f"Order #{order_id} has not been delivered yet.",
        }

    # 檢查是否在 14 天退款期限內
    if order["delivery_date"]:
        days_since_delivery = (
            datetime.date.today() - order["delivery_date"]
        ).days
        if days_since_delivery > 14:
            return {
                "status": "failed",
                "reason": (
                    f"Order #{order_id} was delivered {days_since_delivery} days"
                    " ago, exceeding the 14-day refund window."
                ),
            }

    order["refunded"] = True
    return {
        "status": "success",
        "message": (
            f"Refund of ${order['price']} approved for order #{order_id}."
        ),
        "reason": reason,
    }