import enum
from typing import List, Dict
from collections import Counter

class ValidationError(str, enum.Enum):
    INSUFFICIENT_STAFF = "INSUFFICIENT_STAFF"
    NO_VETERAN_WARNING = "NO_VETERAN_WARNING"
    DOUBLE_BOOKING = "DOUBLE_BOOKING"

def validate_shifts_for_day(
    assignments: List[Dict], # 例: [{"slot_id": 1, "staff_id": 101, "staff_rank": "VETERAN"}, ...]
    slot_definitions: Dict[int, Dict] # 例: {1: {"min_staff": 2}, 2: {"min_staff": 1}}
) -> Dict[int, List[ValidationError]]:
    """
    手動変更された1日分のシフト配列を受け取り、スロット毎の警告を返す。
    
    Returns:
        スロットIDをキーとし、そのスロットのエラーリストを値とする辞書。
        例: {1: ["INSUFFICIENT_STAFF"], 2: []}
    """
    errors = {slot_id: [] for slot_id in slot_definitions.keys()}
    
    # --- 日付全体での重複配置をチェック ---
    staff_counts = Counter(a['staff_id'] for a in assignments)
    doubly_booked_staff = {staff_id for staff_id, count in staff_counts.items() if count > 1}

    # スロット毎に割り当てをグループ化
    assignments_by_slot = {slot_id: [] for slot_id in slot_definitions.keys()}
    for a in assignments:
        if a['slot_id'] in assignments_by_slot:
            assignments_by_slot[a['slot_id']].append(a)

    for slot_id, slot_assignments in assignments_by_slot.items():
        slot_def = slot_definitions.get(slot_id)
        if not slot_def:
            continue

        # --- 人数不足をチェック ---
        if len(slot_assignments) < slot_def.get("min_staff", 1):
            errors[slot_id].append(ValidationError.INSUFFICIENT_STAFF)

        # --- ベテラン不在をチェック ---
        if len(slot_assignments) > 0 and not any(a.get("staff_rank") == "VETERAN" for a in slot_assignments):
            errors[slot_id].append(ValidationError.NO_VETERAN_WARNING)
            
        # --- 重複配置エラーを追加 ---
        if any(a['staff_id'] in doubly_booked_staff for a in slot_assignments):
            errors[slot_id].append(ValidationError.DOUBLE_BOOKING)

    return errors