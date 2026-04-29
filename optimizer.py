from ortools.sat.python import cp_model
from typing import List
from datetime import date, timedelta

import models

class ShiftOptimizer:
    """
    制約充足問題（CSP）としてシフトをモデル化し、OR-Toolsで計算を実行。
    """

    def generate(self, staff: List[models.Staff], off_requests: List[models.OffRequest], slots: List[models.ShiftSlot], start_date: date, end_date: date):
        """
        シフトスケジュールを生成する。
        """
        num_staff = len(staff)
        num_days = (end_date - start_date).days + 1
        num_slots = len(slots)
        dates = [start_date + timedelta(days=d) for d in range(num_days)]

        model = cp_model.CpModel()

        # --- 1. 変数定義 ---
        # work[d, s, p]: d日目のs枠にpスタッフが割り当てられるか
        work = {}
        for d_idx, day in enumerate(dates):
            for s_idx, slot in enumerate(slots):
                for p_idx, person in enumerate(staff):
                    work[(d_idx, s_idx, p_idx)] = model.NewBoolVar(f'work_{d_idx}_{s_idx}_{p_idx}')

        # --- 2. 必須制約 (Hard Constraints) ---

        # 各枠の割り当て人数は、設定されたmin_staffを満たす
        for d_idx in range(num_days):
            for s_idx, slot in enumerate(slots):
                model.Add(sum(work[(d_idx, s_idx, p_idx)] for p_idx in range(num_staff)) >= slot.min_staff)

        # 各枠には最低1名のベテランを配置
        veteran_indices = [i for i, s in enumerate(staff) if s.rank == models.StaffRank.VETERAN]
        for d_idx in range(num_days):
            for s_idx in range(num_slots):
                model.Add(sum(work[(d_idx, s_idx, p_idx)] for p_idx in veteran_indices) >= 1)

        # スタッフの休み希望と重複しない
        for req in off_requests:
            try:
                d_idx = dates.index(req.date)
                p_idx = staff.index(next(s for s in staff if s.id == req.staff_id))
                for s_idx in range(num_slots):
                    model.Add(work[(d_idx, s_idx, p_idx)] == 0)
            except (ValueError, StopIteration):
                pass # 最適化対象外のスタッフや日付の希望は無視
        
        # 1人のスタッフは1日に1つのシフトしか入れない
        for d_idx in range(num_days):
            for p_idx in range(num_staff):
                model.Add(sum(work[(d_idx, s_idx, p_idx)] for s_idx in range(num_slots)) <= 1)

        # --- 3. ソフト制約 (Soft Constraints) ---
        
        # TODO: 全スタッフの総勤務コマ数の差を最小化 (公平性)

        # 「夜間診」の翌日の「午前診」への割り当てを避ける
        try:
            night_slot_idx = next(i for i, s in enumerate(slots) if s.name == "夜間診")
            am_slot_idx = next(i for i, s in enumerate(slots) if s.name == "午前診")
            for d_idx in range(num_days - 1):
                for p_idx in range(num_staff):
                    model.AddBoolOr([
                        work[(d_idx, night_slot_idx, p_idx)].Not(), 
                        work[(d_idx + 1, am_slot_idx, p_idx)].Not()
                    ])
        except StopIteration:
            pass # 夜間診または午前診が存在しない場合はスキップ

        # --- 4. ソルバーの実行 ---
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 30.0 # タイムアウト設定
        status = solver.Solve(model)

        # --- 5. 結果の解析 ---
        assignments = []
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            for d_idx, day in enumerate(dates):
                for s_idx, slot in enumerate(slots):
                    for p_idx, person in enumerate(staff):
                        if solver.Value(work[(d_idx, s_idx, p_idx)]) == 1:
                            assignments.append(
                                models.ShiftAssignmentModel(date=day, slot_id=slot.id, staff_id=person.id)
                            )
            return assignments
        else:
            return [] # 解が見つからなかった場合