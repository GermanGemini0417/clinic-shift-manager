"use client";
import React, { useState } from 'react';

const SLOTS = ["午前診", "午後診", "夜間診"];

export default function OffRequestPage() {
  const [selectedDates, setSelectedDates] = useState<Record<string, string[]>>({});

  const toggleSlot = (date: string, slot: string) => {
    const current = selectedDates[date] || [];
    const next = current.includes(slot)
      ? current.filter(s => s !== slot)
      : [...current, slot];
    setSelectedDates({ ...selectedDates, [date]: next });
  };

  return (
    <div className="p-4 max-w-md mx-auto bg-gray-50 min-h-screen">
      <h1 className="text-xl font-bold mb-4 text-blue-800">休み希望入力</h1>
      <div className="space-y-4">
        {[...Array(7)].map((_, i) => {
          const date = `2026-05-0${i + 1}`;
          return (
            <div key={date} className="bg-white p-3 rounded-lg shadow">
              <p className="font-semibold border-b mb-2">{date}</p>
              <div className="flex gap-2">
                {SLOTS.map(slot => (
                  <button
                    key={slot}
                    onClick={() => toggleSlot(date, slot)}
                    className={`px-3 py-2 rounded-full text-sm border ${
                      selectedDates[date]?.includes(slot)
                      ? "bg-red-500 text-white border-red-500"
                      : "bg-white text-gray-700 border-gray-300"
                    }`}
                  >
                    {slot}
                  </button>
                ))}
              </div>
            </div>
          );
        })}
      </div>
      <button className="w-full mt-6 bg-blue-600 text-white py-3 rounded-lg font-bold shadow-lg">
        希望を送信する
      </button>
    </div>
  );
}