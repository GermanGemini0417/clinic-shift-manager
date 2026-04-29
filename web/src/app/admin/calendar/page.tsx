"use client";
import React from 'react';

// ダミーデータ
const shiftData = [
  { date: "5/1", AM: ["田中", "鈴木"], PM: ["田中", "佐藤"], NIGHT: ["鈴木"] },
  { date: "5/2", AM: ["佐藤"], PM: [], NIGHT: ["田中"] }, // PMが欠員
];

export default function AdminCalendarPage() {
  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">事務シフト管理 (2026年5月)</h1>
        <button className="bg-green-600 text-white px-4 py-2 rounded">自動生成を実行</button>
      </div>
      
      <div className="overflow-x-auto border rounded-lg">
        <table className="min-w-full bg-white">
          <thead className="bg-gray-100">
            <tr>
              <th className="p-3 border">日付</th>
              <th className="p-3 border">午前診</th>
              <th className="p-3 border">午後診</th>
              <th className="p-3 border">夜間診</th>
            </tr>
          </thead>
          <tbody>
            {shiftData.map(day => (
              <tr key={day.date}>
                <td className="p-3 border font-medium text-center">{day.date}</td>
                <td className="p-3 border">
                  {day.AM.map(s => <span key={s} className="block text-sm">{s}</span>)}
                  {day.AM.length < 2 && <span className="text-xs text-red-500">⚠️ 人数不足</span>}
                </td>
                <td className={`p-3 border ${day.PM.length === 0 ? "bg-red-50" : ""}`}>
                  {day.PM.map(s => <span key={s} className="block text-sm">{s}</span>)}
                  {day.PM.length === 0 && <span className="text-xs text-red-600 font-bold">欠員あり</span>}
                </td>
                <td className="p-3 border">
                  {day.NIGHT.map(s => <span key={s} className="block text-sm">{s}</span>)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}