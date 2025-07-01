"use client";

import { useState, useEffect } from "react";
import { format } from "date-fns";
import { Calendar as CalendarIcon, History, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { regionData, codeToText } from 'element-china-area-data';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";

interface HistoryEntry {
  id: string;
  name: string;
  gender: string;
  birth_location: string;
  is_lunar: boolean;
  birth_time?: string; // For Solar: "YYYY-MM-DD HH:MM:SS"
  year?: number;       // For Lunar
  month?: number;      // For Lunar
  day?: number;        // For Lunar
  time?: string;       // For Lunar: "HH:MM:SS"
  province_code?: string;
  city_code?: string;
  area_code?: string;
}

const LUNAR_YEARS = Array.from({ length: 150 }, (_, i) => new Date().getFullYear() - i);
const LUNAR_MONTHS = Array.from({ length: 12 }, (_, i) => i + 1);
const LUNAR_DAYS = Array.from({ length: 30 }, (_, i) => i + 1);

export default function Home() {
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
  const [areas, setAreas] =useState<{ value: string; label: string; }[]>([]);
  
  const [result, setResult] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [history, setHistory] = useState<HistoryEntry[]>([]);

  useEffect(() => {
    try {
      const savedHistory = localStorage.getItem("baziHistory");
      if (savedHistory) setHistory(JSON.parse(savedHistory));
    } catch (error) { console.error("无法读取历史记录:", error); }
  }, []);

  const handleProvinceChange = (provinceCode: string) => {
    setSelectedProvince(provinceCode);
    const province = regionData.find(p => p.value === provinceCode);
    setCities(province?.children || []);
    setSelectedCity("");
    setAreas([]);
    setSelectedArea("");
  };

  const handleCityChange = (cityCode: string) => {
    setSelectedCity(cityCode);
    const city = cities.find(c => c.value === cityCode);
    setAreas(city?.children || []);
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
        // Conditionally add properties based on calendar type
        ...(payload.is_lunar
          ? { year: payload.year, month: payload.month, day: payload.day, time: payload.birth_time }
          : { birth_time: payload.birth_time }),
        province_code: selectedProvince,
        city_code: selectedCity,
        area_code: selectedArea
      };
      
      const updatedHistory = [newEntry, ...history.filter(h => h.name !== newEntry.name)].slice(0, 5);
      setHistory(updatedHistory);
      localStorage.setItem("baziHistory", JSON.stringify(updatedHistory));
    } catch (error) { console.error("无法保存历史记录:", error); }
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
          const province = regionData.find(p => p.value === entry.province_code);
          const city = province?.children?.find(c => c.value === entry.city_code);
          setAreas(city?.children || []);
          if (entry.area_code) {
            setTimeout(() => setSelectedArea(entry.area_code!), 0);
          }
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

    const promise = () => new Promise(async (resolve, reject) => {
      try {
        const response = await fetch("http://127.0.0.1:8000/analyze/stream", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({ error: "无法解析错误信息" }));
          reject(new Error(errorData.detail || `HTTP 错误! 状态码: ${response.status}`));
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

    toast.promise(promise, { loading: '正在请求AI大师分析中...', success: '分析已完成！', error: (err) => `分析失败: ${err}.` });
  };

  return (
    <>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="text-2xl font-bold">☯ 周运势分析</CardTitle>
              <CardDescription>输入以下信息将为你生成个人专属周运势分析报告。（仅供娱乐）</CardDescription>
            </CardHeader>
            <CardContent className="grid gap-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                 <div className="space-y-2"><Label htmlFor="name">姓名 (可选)</Label><Input id="name" placeholder="您的姓名" value={name} onChange={(e) => setName(e.target.value)} /></div>
                 <div className="space-y-2"><Label htmlFor="gender">性别 *</Label><Select onValueChange={setGender} value={gender}><SelectTrigger id="gender"><SelectValue placeholder="请选择性别" /></SelectTrigger><SelectContent><SelectItem value="男">男</SelectItem><SelectItem value="女">女</SelectItem></SelectContent></Select></div>
              </div>
              
              <div className="flex items-center space-x-2">
                <Label htmlFor="calendar-type">公历生日</Label>
                <Switch id="calendar-type" checked={isLunar} onCheckedChange={setIsLunar} />
                <Label htmlFor="calendar-type">农历生日</Label>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>出生日期 *</Label>
                  {isLunar ? (
                     <div className="grid grid-cols-3 gap-2">
                        <Select onValueChange={(v) => setLunarYear(Number(v))} value={String(lunarYear)}><SelectTrigger><SelectValue placeholder="年份" /></SelectTrigger><SelectContent>{LUNAR_YEARS.map(y => <SelectItem key={y} value={String(y)}>{y}年</SelectItem>)}</SelectContent></Select>
                        <Select onValueChange={(v) => setLunarMonth(Number(v))} value={String(lunarMonth)}><SelectTrigger><SelectValue placeholder="月份" /></SelectTrigger><SelectContent>{LUNAR_MONTHS.map(m => <SelectItem key={m} value={String(m)}>{m}月</SelectItem>)}</SelectContent></Select>
                        <Select onValueChange={(v) => setLunarDay(Number(v))} value={String(lunarDay)}><SelectTrigger><SelectValue placeholder="日期" /></SelectTrigger><SelectContent>{LUNAR_DAYS.map(d => <SelectItem key={d} value={String(d)}>{d}日</SelectItem>)}</SelectContent></Select>
                     </div>
                  ) : (
                    <Popover>
                      <PopoverTrigger asChild>
                        <Button variant="outline" className={cn("w-full justify-start text-left font-normal", !date && "text-muted-foreground")}>
                          <CalendarIcon className="mr-2 h-4 w-4" />
                          {date ? format(date, "PPP") : <span>选择日期</span>}
                        </Button>
                      </PopoverTrigger>
                      <PopoverContent className="w-auto p-0"><Calendar mode="single" captionLayout="dropdown" fromYear={1900} toYear={new Date().getFullYear()} selected={date} onSelect={setDate} initialFocus /></PopoverContent>
                    </Popover>
                  )}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="birth-time">出生时间 *</Label>
                  <Input id="birth-time" type="time" step="1" value={time} onChange={(e) => setTime(e.target.value)} />
                </div>
              </div>
              
              <div className="space-y-2">
                <Label>出生地点 *</Label>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <Select onValueChange={handleProvinceChange} value={selectedProvince}><SelectTrigger><SelectValue placeholder="请选择省份" /></SelectTrigger><SelectContent>{regionData.map(p => <SelectItem key={p.value} value={p.value}>{p.label}</SelectItem>)}</SelectContent></Select>
                    <Select onValueChange={handleCityChange} value={selectedCity} disabled={!selectedProvince}><SelectTrigger><SelectValue placeholder="请选择城市" /></SelectTrigger><SelectContent>{cities.map(c => <SelectItem key={c.value} value={c.value}>{c.label}</SelectItem>)}</SelectContent></Select>
                    <Select onValueChange={setSelectedArea} value={selectedArea} disabled={!selectedCity}><SelectTrigger><SelectValue placeholder="请选择地区" /></SelectTrigger><SelectContent>{areas.map(a => <SelectItem key={a.value} value={a.value}>{a.label}</SelectItem>)}</SelectContent></Select>
                </div>
              </div>
            </CardContent>
            <CardFooter><Button onClick={handleAnalysis} disabled={isLoading} className="w-full">{isLoading ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> 分析中...</> : "开始分析"}</Button></CardFooter>
          </Card>
        </div>
        
        <div className="space-y-8">
            {history.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center"><History className="mr-2 h-5 w-5" /> 最近记录</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  {history.map(entry => {
                    const displayDate = entry.is_lunar
                      ? `农历 ${entry.year}-${entry.month}-${entry.day}`
                      : entry.birth_time ? format(new Date(entry.birth_time), "yyyy-MM-dd") : '未知日期';
                    
                    return (
                      <Button key={entry.id} variant="ghost" className="w-full justify-start h-auto text-left" onClick={() => fillFromHistory(entry)}>
                        <div>
                          <div><strong>{entry.name}</strong> - {entry.birth_location}</div>
                          <div className="text-muted-foreground text-sm">{displayDate}</div>
                        </div>
                      </Button>
                    );
                  })}
                </CardContent>
              </Card>
            )}
        </div>
      </div>
      
      {(isLoading || result) && (
        <Card className="mt-8">
          <CardHeader><CardTitle>分析结果</CardTitle></CardHeader>
          <CardContent>
            <div className="prose dark:prose-invert max-w-none text-sm leading-relaxed">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {result}
              </ReactMarkdown>
            </div>
            {isLoading && !result && <div className="flex justify-center items-center h-20"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>}
          </CardContent>
        </Card>
      )}
    </>
  );
}