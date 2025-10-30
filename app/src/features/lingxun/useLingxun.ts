"use client";
import { useEffect, useState } from "react";
import { flushSync } from "react-dom";
import { format } from "date-fns";
import { toast } from "sonner";
import { regionData, codeToText } from "element-china-area-data";
import type { HistoryEntry } from "@/features/lingxun/types";

export function useLingxun() {
  const [name, setName] = useState("");
  const [gender, setGender] = useState("");
  const [date, setDate] = useState<Date | undefined>(new Date());
  const [time, setTime] = useState("12:00:00");
  const [isLunar, setIsLunar] = useState(false);
  const [lunarYear, setLunarYear] = useState(new Date().getFullYear());
  const [lunarMonth, setLunarMonth] = useState(1);
  const [lunarDay, setLunarDay] = useState(1);
  const [selectedProvince, setSelectedProvince] = useState("");
  const [selectedCity, setSelectedCity] = useState("");
  const [selectedArea, setSelectedArea] = useState("");
  const [cities, setCities] = useState<{ value: string; label: string; children?: any[] }[]>([]);
  const [areas, setAreas] = useState<{ value: string; label: string }[]>([]);
  const [result, setResult] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [history, setHistory] = useState<HistoryEntry[]>([]);

  useEffect(() => {
    try {
      const savedHistory = localStorage.getItem("baziHistory");
      if (savedHistory) setHistory(JSON.parse(savedHistory));
    } catch (error) {
      console.error("无法读取历史记录:", error);
    }
  }, []);

  const handleProvinceChange = (provinceCode: string) => {
    setSelectedProvince(provinceCode);
    const province = regionData.find((p) => p.value === provinceCode);
    setCities(province?.children || []);
    setSelectedCity("");
    setAreas([]);
    setSelectedArea("");
  };

  const handleCityChange = (cityCode: string) => {
    setSelectedCity(cityCode);
    const city = cities.find((c) => c.value === cityCode);
    setAreas((city?.children || []) as any);
    setSelectedArea("");
  };

  const saveHistory = (payload: any) => {
    try {
      const newEntry: HistoryEntry = {
        id: new Date().toISOString(),
        name: payload.name,
        gender: payload.gender,
        birth_location: payload.birth_location,
        is_lunar: payload.is_lunar,
        ...(payload.is_lunar
          ? { year: payload.year, month: payload.month, day: payload.day, time: payload.birth_time }
          : { birth_time: payload.birth_time }),
        province_code: selectedProvince,
        city_code: selectedCity,
        area_code: selectedArea,
      };
      const updatedHistory = [newEntry, ...history.filter((h) => h.name !== newEntry.name)].slice(0, 5);
      setHistory(updatedHistory);
      localStorage.setItem("baziHistory", JSON.stringify(updatedHistory));
    } catch (error) {
      console.error("无法保存历史记录:", error);
    }
  };

  const fillFromHistory = (entry: HistoryEntry) => {
    setName(entry.name);
    setGender(entry.gender);
    setIsLunar(entry.is_lunar);
    if (entry.is_lunar) {
      setLunarYear(entry.year!);
      setLunarMonth(entry.month!);
      setLunarDay(entry.day!);
      setTime(entry.time!);
    } else {
      const dateTime = new Date(entry.birth_time!);
      setDate(dateTime);
      setTime(format(dateTime, "HH:mm:ss"));
    }
    if (entry.province_code) {
      handleProvinceChange(entry.province_code);
      if (entry.city_code) {
        setTimeout(() => {
          setSelectedCity(entry.city_code!);
          const province = (regionData as any[]).find((p) => p.value === entry.province_code);
          const city = province?.children?.find((c: any) => c.value === entry.city_code);
          setAreas(city?.children || []);
          if (entry.area_code) setTimeout(() => setSelectedArea(entry.area_code!), 0);
        }, 0);
      }
    }
  };

  const handleAnalysis = async () => {
    if (!gender || (!isLunar && !date) || !selectedProvince || !selectedCity || !selectedArea || !time) {
      toast.error("请填写所有必填字段", { description: "性别、时间及省市区都不能为空。" });
      return;
    }

    let payload: any;
    const commonPayload = {
      name: name || "未填写",
      gender,
      birth_location: `${codeToText[selectedProvince]}/${codeToText[selectedCity]}/${codeToText[selectedArea]}`,
    };

    if (isLunar) {
      payload = {
        ...commonPayload,
        is_lunar: true,
        year: lunarYear,
        month: lunarMonth,
        day: lunarDay,
        birth_time: time,
      };
    } else {
      if (!date) {
        toast.error("请选择公历出生日期");
        return;
      }
      payload = {
        ...commonPayload,
        is_lunar: false,
        birth_time: `${format(date, "yyyy-MM-dd")} ${time}`,
      };
    }

    setIsLoading(true);
    setResult("");
    saveHistory(payload);

    try {
      console.log("[handleAnalysis] 开始请求");

      const response = await fetch("http://127.0.0.1:8000/analyze/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      console.log("[handleAnalysis] 收到响应头, 状态:", response.status);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error("无法获取reader");
      }

      const decoder = new TextDecoder();
      let fullText = "";
      let chunkCount = 0;
      let firstChunk = true;  // ✅ 关键：标记是否收到第一个chunk

      console.log("[handleAnalysis] 开始读取 chunks");

      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          console.log(`[handleAnalysis] ✅ 完成! 共 ${chunkCount} chunks`);
          break;
        }

        if (value) {
          const chunk = decoder.decode(value, { stream: true });
          chunkCount++;

          console.log(`[handleAnalysis] chunk ${chunkCount}: ${chunk.substring(0, 50)}`);

          fullText += chunk;

          // ✅ 使用 flushSync 强制同步更新，确保每个chunk都立即渲染
          flushSync(() => {
            setResult(fullText);
          });

          // ✅ 关键：收到第一个 chunk 时立即关闭加载状态
          if (firstChunk) {
            firstChunk = false;
            flushSync(() => {
              setIsLoading(false);
            });
            console.log("[handleAnalysis] 🎉 收到第一个chunk，取消加载状态");
          }
        }
      }

      setIsLoading(false);  // 最后保险地关闭一次
      toast.success("分析已完成！");
      console.log("[handleAnalysis] 全部完成");
    } catch (err) {
      setIsLoading(false);
      const errorMessage = err instanceof Error ? err.message : "未知错误";
      console.error("[handleAnalysis] 错误:", errorMessage);
      toast.error(`分析失败: ${errorMessage}`);
    }
  };

  return {
    name,
    setName,
    gender,
    setGender,
    date,
    setDate,
    time,
    setTime,
    isLunar,
    setIsLunar,
    lunarYear,
    setLunarYear,
    lunarMonth,
    setLunarMonth,
    lunarDay,
    setLunarDay,
    selectedProvince,
    selectedCity,
    selectedArea,
    cities,
    areas,
    result,
    isLoading,
    history,
    handleProvinceChange,
    handleCityChange,
    handleAnalysis,
    fillFromHistory,
    setSelectedArea,
  };
}