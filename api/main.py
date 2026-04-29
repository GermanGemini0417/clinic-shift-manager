from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import date

import models, optimizer, validator
from models import SessionLocal, engine

# データベーステーブルを作成
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Clinic Shift Manager API",
    description="クリニックのシフト作成・管理システムAPI",
    version="1.0.0",
)

# 設計書に基づきCORSを設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 本番環境ではフロントエンドのURLに制限してください
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DBセッションを取得するための依存関係
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to Clinic Shift Manager API"}

@app.post("/shifts/generate", response_model=List[models.ShiftAssignmentModel])
def generate_shifts_endpoint(start_date: date, end_date: date, db: Session = Depends(get_db)):
    """
    【自動生成】指定された期間のシフトを自動生成する。
    """
    all_staff = db.query(models.Staff).all()
    off_requests = db.query(models.OffRequest).filter(models.OffRequest.date.between(start_date, end_date)).all()
    slots = db.query(models.ShiftSlot).all()

    shift_assignments = optimizer.ShiftOptimizer().generate(
        staff=all_staff,
        off_requests=off_requests,
        slots=slots,
        start_date=start_date,
        end_date=end_date
    )

    if not shift_assignments:
        raise HTTPException(status_code=400, detail="有効なシフトスケジュールを生成できませんでした。")

    # TODO: 生成されたシフトをDBにドラフトとして保存する処理
    return shift_assignments

@app.get("/shifts", response_model=Dict[str, Dict[str, List[int]]])
def get_shifts(start_date: date, end_date: date, db: Session = Depends(get_db)):
    """
    指定された期間の確定シフトを取得する。フロントエンドのカレンダーで扱いやすい形式で返却。
    """
    assignments = db.query(models.ShiftAssignment).filter(models.ShiftAssignment.date.between(start_date, end_date)).all()
    
    # 形式: { "2026-05-01": { "1": [101, 102], "2": [103] } }
    shift_map = {}
    for assign in assignments:
        date_str = assign.date.isoformat()
        slot_id_str = str(assign.slot_id)
        if date_str not in shift_map:
            shift_map[date_str] = {}
        if slot_id_str not in shift_map[date_str]:
            shift_map[date_str][slot_id_str] = []
        shift_map[date_str][slot_id_str].append(assign.staff_id)
        
    return shift_map

@app.put("/shifts/update")
def update_shift(assignment: models.ShiftAssignmentModel, db: Session = Depends(get_db)):
    """
    【手動微調整】特定のシフト割り当てを手動で更新・検証する。
    """
    # TODO: 1. 対象日の現在のシフト状態を取得
    # TODO: 2. 変更を適用
    # TODO: 3. バリデーターを呼び出して検証
    validation_errors = validator.validate_shifts_for_day([], {}) # 動作確認のためダミー引数を設定
    # TODO: 4. 検証OKならDBに保存
    return {"status": "updated", "validation_errors": validation_errors}