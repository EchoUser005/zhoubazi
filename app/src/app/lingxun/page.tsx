"use client";

import { useLingxun } from "@/features/lingxun/useLingxun";
import { LingxunForm } from "@/features/lingxun/components/LingxunForm";
import { ResultPanel } from "@/features/lingxun/components/ResultPanel";
import { HistoryList } from "@/features/lingxun/components/HistoryList";

export default function LingxunPage() {
  const hook = useLingxun();

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 p-6">
      <div className="lg:col-span-2 space-y-6">
        <LingxunForm
          name={hook.name} setName={hook.setName}
          gender={hook.gender} setGender={hook.setGender}
          isLunar={hook.isLunar} setIsLunar={hook.setIsLunar}
          date={hook.date} setDate={hook.setDate}
          time={hook.time} setTime={hook.setTime}
          lunarYear={hook.lunarYear} setLunarYear={hook.setLunarYear}
          lunarMonth={hook.lunarMonth} setLunarMonth={hook.setLunarMonth}
          lunarDay={hook.lunarDay} setLunarDay={hook.setLunarDay}
          selectedProvince={hook.selectedProvince}
          selectedCity={hook.selectedCity}
          selectedArea={hook.selectedArea}
          cities={hook.cities}
          areas={hook.areas}
          handleProvinceChange={hook.handleProvinceChange}
          handleCityChange={hook.handleCityChange}
          setSelectedArea={hook.setSelectedArea}
          handleAnalysis={hook.handleAnalysis}
          isLoading={hook.isLoading}
        />
        <ResultPanel isLoading={hook.isLoading} result={hook.result} />
      </div>

      <div className="space-y-6">
        <HistoryList history={hook.history} onSelect={hook.fillFromHistory} />
      </div>
    </div>
  );
}