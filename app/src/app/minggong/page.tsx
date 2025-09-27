"use client";

import { useState, useEffect } from "react";
import { format } from "date-fns";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverTrigger, PopoverContent } from "@/components/ui/popover";
import { Calendar as CalendarIcon } from "lucide-react";
import { Select, SelectTrigger, SelectContent, SelectItem, SelectValue } from "@/components/ui/select";
import { regionData } from "element-china-area-data";
import { cn } from "@/lib/utils";

export default function MingGongPage() {
  // 四柱（可直接编辑）
  const [year, setYear] = useState("");
  const [month, setMonth] = useState("");
  const [day, setDay] = useState("");
  const [hour, setHour] = useState("");

  // 生成四柱的输入：公历 + 时间 + 地区
  const [date, setDate] = useState<Date | undefined>(new Date());
  const [time, setTime] = useState("12:00:00");
  const [province, setProvince] = useState("");
  const [city, setCity] = useState("");
  const [area, setArea] = useState("");
  const [cities, setCities] = useState<{ value: string; label: string; children?: any[] }[]>([]);
  const [areas, setAreas] = useState<{ value: string; label: string }[]>([]);
  const [loading, setLoading] = useState(false);

  // 新增：读取/展示命主配置
  const [owner, setOwner] = useState<any | null>(null);
  const [loadingCfg, setLoadingCfg] = useState(true);
  const [cfgError, setCfgError] = useState<string | null>(null);

  useEffect(() => {
    // 首次进入时读取 owner.yaml
    const loadCfg = async () => {
      setLoadingCfg(true);
      setCfgError(null);
      try {
        const resp = await fetch("http://127.0.0.1:8000/owner_config");
        const data = await resp.json();
        if (!resp.ok) throw new Error(data?.error || "读取配置失败");
        setOwner(data.config || null);

        // 若有配置，则直接用该配置调用后端计算四柱并填充
        if (data?.config) {
          const calcResp = await fetch("http://127.0.0.1:8000/calc_bazi", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data.config),
          });
          const calc = await calcResp.json();
          if (calcResp.ok) {
            setYear(calc.year || "");
            setMonth(calc.month || "");
            setDay(calc.day || "");
            setHour(calc.hour || "");
          }
        }
      } catch (e: any) {
        setCfgError(e?.message || String(e));
      } finally {
        setLoadingCfg(false);
      }
    };
    loadCfg();
  }, []);

  const handleProvinceChange = (code: string) => {
    setProvince(code);
    const p = regionData.find((x) => x.value === code);
    setCities(p?.children || []);
    setCity("");
    setAreas([]);
    setArea("");
  };
  const handleCityChange = (code: string) => {
    setCity(code);
    const c = cities.find((x) => x.value === code);
    setAreas((c?.children || []) as any);
    setArea("");
  };

  const genFromDate = async () => {
    if (!date || !time || !province || !city || !area) {
      alert("请选择日期、时间、省市区");
      return;
    }
    setLoading(true);
    try {
      // 直接复用后端的计算逻辑
      const payload = {
        name: "命宫配置",
        gender: "男",
        is_lunar: false,
        birth_time: `${format(date, "yyyy-MM-dd")} ${time}`,
        birth_location: "省/市/区", // 后端会解析城市名，这里占位；更精确可拼接汉字名称
      };
      // 可选：把省市区中文名传给后端，你若需要可调整后端解析策略
      const resp = await fetch("http://127.0.0.1:8000/calc_bazi", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await resp.json();
      if (!resp.ok) {
        throw new Error(data?.error || "计算失败");
      }
      setYear(data.year || "");
      setMonth(data.month || "");
      setDay(data.day || "");
      setHour(data.hour || "");
    } catch (e) {
      alert(`生成失败：${e}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-[calc(100vh-56px)] px-6 py-10 mx-auto max-w-4xl">
      {/* 新增：命主配置预览 */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="text-xl font-semibold">当前命主配置（只读）</CardTitle>
          <CardDescription>来源：config/owner.yaml。进入页面时自动读取；若为空，请检查文件是否存在。</CardDescription>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          {loadingCfg ? (
            <div>读取配置中...</div>
          ) : cfgError ? (
            <div className="text-red-500">读取失败：{cfgError}</div>
          ) : owner ? (
            <>
              <div>姓名：{owner.name ?? "-"}</div>
              <div>性别：{owner.gender ?? "-"}</div>
              <div>是否农历：{String(owner.is_lunar ?? false)}</div>
              {owner.birth_time ? (
                <div>公历出生时间：{owner.birth_time}</div>
              ) : (
                <div>
                  农历：{owner.year ?? "-"}年 {owner.month ?? "-"}月 {owner.day ?? "-"}日
                </div>
              )}
              <div>出生地：{owner.birth_location ?? "-"}</div>
            </>
          ) : (
            <div className="text-muted-foreground">未找到命主配置（owner.yaml）。</div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-2xl font-bold">命宫配置</CardTitle>
          <CardDescription>仅模仿 UI 样式，配置项暂时只包含四柱。支持从日期生成四柱。</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-6">
          {/* 四柱配置（可编辑） */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div>
              <Label>年柱</Label>
              <Input value={year} onChange={(e) => setYear(e.target.value)} placeholder="如：辛巳" />
            </div>
            <div>
              <Label>月柱</Label>
              <Input value={month} onChange={(e) => setMonth(e.target.value)} placeholder="如：庚子" />
            </div>
            <div>
              <Label>日柱</Label>
              <Input value={day} onChange={(e) => setDay(e.target.value)} placeholder="如：辛酉" />
            </div>
            <div>
              <Label>时柱</Label>
              <Input value={hour} onChange={(e) => setHour(e.target.value)} placeholder="如：乙未" />
            </div>
          </div>
          {/* 通过日期生成四柱（仿现有 UI） */}
          <div className="grid gap-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>出生日期</Label>
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
              </div>
              <div className="space-y-2">
                <Label>出生时间</Label>
                <Input type="time" step="1" value={time} onChange={(e) => setTime(e.target.value)} />
              </div>
            </div>

            <div className="space-y-2">
              <Label>出生地点</Label>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                <Select value={province} onValueChange={handleProvinceChange}>
                  <SelectTrigger><SelectValue placeholder="省份" /></SelectTrigger>
                  <SelectContent>
                    {regionData.map((p) => <SelectItem key={p.value} value={p.value}>{p.label}</SelectItem>)}
                  </SelectContent>
                </Select>
                <Select value={city} onValueChange={handleCityChange} disabled={!province}>
                  <SelectTrigger><SelectValue placeholder="城市" /></SelectTrigger>
                  <SelectContent>
                    {cities.map((c) => <SelectItem key={c.value} value={c.value}>{c.label}</SelectItem>)}
                  </SelectContent>
                </Select>
                <Select value={area} onValueChange={setArea} disabled={!city}>
                  <SelectTrigger><SelectValue placeholder="地区" /></SelectTrigger>
                  <SelectContent>
                    {areas.map((a) => <SelectItem key={a.value} value={a.value}>{a.label}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="flex gap-3">
              <Button onClick={genFromDate} disabled={loading}>
                {loading ? "生成中..." : "根据日期生成四柱"}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </main>
  );
}