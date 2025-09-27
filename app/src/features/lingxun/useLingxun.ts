"use client";

import { useEffect, useState } from "react";
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

    const commonPayload = {
      name: name || "未填写",
      gender,
      birth_location: `${codeToText[selectedProvince]}/${codeToText[selectedCity]}/${codeToText[selectedArea]}`,
    };

    let payload: any;
    if (isLunar) {
      payload = { ...commonPayload, is_lunar: true, year: lunarYear, month: lunarMonth, day: lunarDay, birth_time: time };
    } else {
      if (!date) {
        toast.error("请选择公历出生日期");
        return;
      }
      payload = { ...commonPayload, is_lunar: false, birth_time: `${format(date, "yyyy-MM-dd")} ${time}` };
    }

    setIsLoading(true);
    setResult("");

    const promise = () =>
      new Promise(async (resolve, reject) => {
        try {
          const response = await fetch("http://127.0.0.1:8000/analyze/stream", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
          });
          if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: "无法解析错误信息" }));
            reject(new Error((errorData as any).detail || `HTTP 错误! 状态码: ${response.status}`));
            return;
          }
          saveHistory(payload);
          const reader = response.body?.getReader();
          if (!reader) {
            reject(new Error("无法获取响应读取器"));
            return;
          }
          const decoder = new TextDecoder();
          let done = false;
          while (!done) {
            const { value, done: readerDone } = await reader.read();
            done = readerDone;
            const chunk = decoder.decode(value, { stream: true });
            setResult((prev) => prev + chunk);
          }
          resolve("分析完成");
        } catch (err) {
          const errorMessage = err instanceof Error ? err.message : "发生了未知错误";
          reject(errorMessage);
        } finally {
          setIsLoading(false);
        }
      });

    toast.promise(promise, {
      loading: "正在请求AI大师分析中...",
      success: "分析已完成！",
      error: (err) => `分析失败: ${err}.`,
    });
  };

  return {
    name, setName,
    gender, setGender,
    date, setDate,
    time, setTime,
    isLunar, setIsLunar,
    lunarYear, setLunarYear,
    lunarMonth, setLunarMonth,
    lunarDay, setLunarDay,
    selectedProvince, selectedCity, selectedArea,
    cities, areas,
    result, isLoading, history,
    handleProvinceChange, handleCityChange,
    handleAnalysis, fillFromHistory, setSelectedArea,
  };
}