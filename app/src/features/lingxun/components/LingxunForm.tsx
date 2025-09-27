"use client";

import { format } from "date-fns";
import { Calendar as CalendarIcon } from "lucide-react";
import { LUNAR_DAYS, LUNAR_MONTHS, LUNAR_YEARS } from "@/features/lingxun/types";
import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { cn } from "@/lib/utils";
import { regionData } from "element-china-area-data";

type Props = {
  name: string; setName: (v: string) => void;
  gender: string; setGender: (v: string) => void;
  isLunar: boolean; setIsLunar: (v: boolean) => void;
  date: Date | undefined; setDate: (d?: Date) => void;
  time: string; setTime: (v: string) => void;
  lunarYear: number; setLunarYear: (n: number) => void;
  lunarMonth: number; setLunarMonth: (n: number) => void;
  lunarDay: number; setLunarDay: (n: number) => void;

  selectedProvince: string;
  selectedCity: string;
  selectedArea: string;
  cities: { value: string; label: string; children?: any[] }[];
  areas: { value: string; label: string }[];

  handleProvinceChange: (code: string) => void;
  handleCityChange: (code: string) => void;
  setSelectedArea: (code: string) => void;

  handleAnalysis: () => Promise<void> | void;
  isLoading: boolean;
};

export function LingxunForm(props: Props) {
  const {
    name, setName, gender, setGender, isLunar, setIsLunar,
    date, setDate, time, setTime,
    lunarYear, setLunarYear, lunarMonth, setLunarMonth, lunarDay, setLunarDay,
    selectedProvince, selectedCity, selectedArea, cities, areas,
    handleProvinceChange, handleCityChange, setSelectedArea,
    handleAnalysis, isLoading
  } = props;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-2xl font-bold">☯ 周运势分析</CardTitle>
        <CardDescription>输入以下信息将为你生成个人专属周运势分析报告。（仅供娱乐）</CardDescription>
      </CardHeader>
      <CardContent className="grid gap-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="name">姓名 (可选)</Label>
            <Input id="name" placeholder="您的姓名" value={name} onChange={(e) => setName(e.target.value)} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="gender">性别 *</Label>
            <Select onValueChange={setGender} value={gender}>
              <SelectTrigger id="gender">
                <SelectValue placeholder="请选择性别" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="男">男</SelectItem>
                <SelectItem value="女">女</SelectItem>
              </SelectContent>
            </Select>
          </div>
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
                <Select onValueChange={(v) => setLunarYear(Number(v))} value={String(lunarYear)}>
                  <SelectTrigger><SelectValue placeholder="年份" /></SelectTrigger>
                  <SelectContent>
                    {LUNAR_YEARS.map((y) => <SelectItem key={y} value={String(y)}>{y}年</SelectItem>)}
                  </SelectContent>
                </Select>
                <Select onValueChange={(v) => setLunarMonth(Number(v))} value={String(lunarMonth)}>
                  <SelectTrigger><SelectValue placeholder="月份" /></SelectTrigger>
                  <SelectContent>
                    {LUNAR_MONTHS.map((m) => <SelectItem key={m} value={String(m)}>{m}月</SelectItem>)}
                  </SelectContent>
                </Select>
                <Select onValueChange={(v) => setLunarDay(Number(v))} value={String(lunarDay)}>
                  <SelectTrigger><SelectValue placeholder="日期" /></SelectTrigger>
                  <SelectContent>
                    {LUNAR_DAYS.map((d) => <SelectItem key={d} value={String(d)}>{d}日</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
            ) : (
              <Popover>
                <PopoverTrigger asChild>
                  <Button variant="outline" className={cn("w-full justify-start text-left font-normal", !date && "text-muted-foreground")}>
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {date ? format(date, "PPP") : <span>选择日期</span>}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0">
                  <Calendar mode="single" captionLayout="dropdown" fromYear={1900} toYear={new Date().getFullYear()} selected={date} onSelect={setDate} initialFocus />
                </PopoverContent>
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
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
            <Select value={selectedProvince} onValueChange={handleProvinceChange}>
              <SelectTrigger><SelectValue placeholder="省份" /></SelectTrigger>
              <SelectContent>
                {regionData.map((p) => <SelectItem key={p.value} value={p.value}>{p.label}</SelectItem>)}
              </SelectContent>
            </Select>
            <Select value={selectedCity} onValueChange={handleCityChange} disabled={!selectedProvince}>
              <SelectTrigger><SelectValue placeholder="城市" /></SelectTrigger>
              <SelectContent>
                {cities.map((c) => <SelectItem key={c.value} value={c.value}>{c.label}</SelectItem>)}
              </SelectContent>
            </Select>
            <Select value={selectedArea} onValueChange={setSelectedArea} disabled={!selectedCity}>
              <SelectTrigger><SelectValue placeholder="地区" /></SelectTrigger>
              <SelectContent>
                {areas.map((a) => <SelectItem key={a.value} value={a.value}>{a.label}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>
        </div>

        <Button onClick={handleAnalysis} disabled={isLoading}>
          {isLoading ? "分析中..." : "开始分析"}
        </Button>
      </CardContent>
    </Card>
  );
}