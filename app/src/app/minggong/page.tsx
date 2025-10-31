"use client";

import { useState, useEffect } from "react";
import { format } from "date-fns";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverTrigger, PopoverContent } from "@/components/ui/popover";
import { Calendar as CalendarIcon, Save, RefreshCw } from "lucide-react";
import { Select, SelectTrigger, SelectContent, SelectItem, SelectValue } from "@/components/ui/select";
import { regionData } from "element-china-area-data";
import { cn } from "@/lib/utils";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Checkbox } from "@/components/ui/checkbox";
import { API_BASE_URL } from "@/config/api";

export default function MingGongPage() {
  // 命主配置字段
  const [name, setName] = useState("");
  const [gender, setGender] = useState("男");
  const [isLunar, setIsLunar] = useState(false);
  const [isTai, setIsTai] = useState(false);
  const [currentCity, setCurrentCity] = useState("");

  // 公历输入
  const [date, setDate] = useState<Date | undefined>(new Date());
  const [time, setTime] = useState("12:00:00");

  // 农历输入
  const [lunarYear, setLunarYear] = useState("");
  const [lunarMonth, setLunarMonth] = useState("");
  const [lunarDay, setLunarDay] = useState("");

  // 出生地点
  const [province, setProvince] = useState("");
  const [city, setCity] = useState("");
  const [area, setArea] = useState("");
  const [cities, setCities] = useState<{ value: string; label: string; children?: any[] }[]>([]);
  const [areas, setAreas] = useState<{ value: string; label: string }[]>([]);

  // 计算出的四柱
  const [year, setYear] = useState("");
  const [month, setMonth] = useState("");
  const [day, setDay] = useState("");
  const [hour, setHour] = useState("");

  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [loadingCfg, setLoadingCfg] = useState(true);
  const [cfgError, setCfgError] = useState<string | null>(null);

  // API Keys 配置
  const [geminiApiKey, setGeminiApiKey] = useState("");
  const [deepseekApiKey, setDeepseekApiKey] = useState("");
  const [llmProvider, setLlmProvider] = useState("gemini");
  const [savingSettings, setSavingSettings] = useState(false);

  useEffect(() => {
    // 首次进入时读取 owner.yaml 并填充表单
    const loadCfg = async () => {
      setLoadingCfg(true);
      setCfgError(null);
      try {
        const resp = await fetch(`${API_BASE_URL}/owner_config`);
        const data = await resp.json();
        if (!resp.ok) throw new Error(data?.error || "读取配置失败");

        const cfg = data.config;
        if (cfg) {
          // 填充表单字段
          setName(cfg.name || "");
          setGender(cfg.gender || "男");
          setIsLunar(cfg.is_lunar || false);
          setIsTai(cfg.isTai || false);
          setCurrentCity(cfg.city || "");

          // 填充出生时间
          if (cfg.is_lunar) {
            setLunarYear(String(cfg.year || ""));
            setLunarMonth(String(cfg.month || ""));
            setLunarDay(String(cfg.day || ""));
          } else if (cfg.birth_time) {
            const [dateStr, timeStr] = cfg.birth_time.split(" ");
            if (dateStr) setDate(new Date(dateStr));
            if (timeStr) setTime(timeStr);
          }

          // 解析出生地点
          if (cfg.birth_location) {
            const parts = cfg.birth_location.split("/");
            if (parts.length >= 1) {
              const prov = regionData.find(p => p.label === parts[0]);
              if (prov) {
                setProvince(prov.value);
                setCities(prov.children || []);

                if (parts.length >= 2 && prov.children) {
                  const ct = prov.children.find((c: any) => c.label === parts[1]);
                  if (ct) {
                    setCity(ct.value);
                    setAreas(ct.children || []);

                    if (parts.length >= 3 && ct.children) {
                      const ar = ct.children.find((a: any) => a.label === parts[2]);
                      if (ar) setArea(ar.value);
                    }
                  }
                }
              }
            }
          }

          // 计算四柱
          const calcResp = await fetch(`${API_BASE_URL}/calc_bazi`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(cfg),
          });
          const calc = await calcResp.json();
          if (calcResp.ok) {
            setYear(calc.year || "");
            setMonth(calc.month || "");
            setDay(calc.day || "");
            setHour(calc.hour || "");
          }
        }

        // 加载 API Keys 配置
        const settingsResp = await fetch(`${API_BASE_URL}/settings`);
        const settingsData = await settingsResp.json();
        if (settingsResp.ok) {
          setLlmProvider(settingsData.llm_provider || "gemini");
          // 不显示真实的 key，只显示占位符
          if (settingsData.has_gemini_key) {
            setGeminiApiKey("***已配置***");
          }
          if (settingsData.has_deepseek_key) {
            setDeepseekApiKey("***已配置***");
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

  const calcBazi = async () => {
    setLoading(true);
    try {
      // 构建payload
      const provinceLabel = regionData.find(p => p.value === province)?.label || "";
      const cityLabel = cities.find(c => c.value === city)?.label || "";
      const areaLabel = areas.find(a => a.value === area)?.label || "";
      const birthLocation = `${provinceLabel}/${cityLabel}/${areaLabel}`;

      const payload: any = {
        name: name || "命主",
        gender,
        birth_location: birthLocation,
        city: currentCity || "",
        isTai,
        is_lunar: isLunar,
      };

      if (isLunar) {
        payload.year = parseInt(lunarYear) || 0;
        payload.month = parseInt(lunarMonth) || 0;
        payload.day = parseInt(lunarDay) || 0;
      } else {
        if (!date) {
          alert("请选择出生日期");
          return;
        }
        payload.birth_time = `${format(date, "yyyy-MM-dd")} ${time}`;
      }

      const resp = await fetch(`${API_BASE_URL}/calc_bazi`, {
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
      alert(`计算失败：${e}`);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!province || !city || !area) {
      alert("请选择完整的出生地点（省/市/区）");
      return;
    }
    if (!gender) {
      alert("请选择性别");
      return;
    }

    setSaving(true);
    try {
      // 构建保存的payload
      const provinceLabel = regionData.find(p => p.value === province)?.label || "";
      const cityLabel = cities.find(c => c.value === city)?.label || "";
      const areaLabel = areas.find(a => a.value === area)?.label || "";
      const birthLocation = `${provinceLabel}/${cityLabel}/${areaLabel}`;

      const payload: any = {
        name: name || "命主",
        gender,
        birth_location: birthLocation,
        city: currentCity || "",
        isTai,
        is_lunar: isLunar,
      };

      if (isLunar) {
        if (!lunarYear || !lunarMonth || !lunarDay) {
          alert("请输入完整的农历日期（年/月/日）");
          return;
        }
        payload.year = parseInt(lunarYear);
        payload.month = parseInt(lunarMonth);
        payload.day = parseInt(lunarDay);
      } else {
        if (!date) {
          alert("请选择出生日期");
          return;
        }
        payload.birth_time = `${format(date, "yyyy-MM-dd")} ${time}`;
      }

      const resp = await fetch(`${API_BASE_URL}/owner_config`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!resp.ok) {
        const data = await resp.json();
        throw new Error(data?.error || "保存失败");
      }

      alert("保存成功！配置已更新到 config/owner.yaml");

      // 重新计算四柱
      await calcBazi();
    } catch (e) {
      alert(`保存失败：${e}`);
    } finally {
      setSaving(false);
    }
  };

  const handleSaveSettings = async () => {
    setSavingSettings(true);
    try {
      const payload: any = {
        llm_provider: llmProvider,
      };

      // 只有当输入的不是占位符时才更新
      if (geminiApiKey && !geminiApiKey.includes("***")) {
        payload.gemini_api_key = geminiApiKey;
      }
      if (deepseekApiKey && !deepseekApiKey.includes("***")) {
        payload.deepseek_api_key = deepseekApiKey;
      }

      const resp = await fetch(`${API_BASE_URL}/settings`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!resp.ok) {
        const data = await resp.json();
        throw new Error(data?.error || "保存失败");
      }

      alert("API Keys 配置已保存！重启后端服务即可生效");
    } catch (e) {
      alert(`保存失败：${e}`);
    } finally {
      setSavingSettings(false);
    }
  };

  if (loadingCfg) {
    return (
      <main className="min-h-[calc(100vh-56px)] px-6 py-10 mx-auto max-w-4xl">
        <div className="text-center py-20">加载配置中...</div>
      </main>
    );
  }

  return (
    <main className="min-h-[calc(100vh-56px)] px-6 py-10 mx-auto max-w-4xl space-y-6">
      {/* API Keys 配置 */}
      <Card>
        <CardHeader>
          <CardTitle className="text-xl font-bold">API Keys 配置</CardTitle>
          <CardDescription>
            配置 Gemini 和 DeepSeek 的 API Keys，保存后重启后端服务即可生效
          </CardDescription>
        </CardHeader>
        <CardContent className="grid gap-6">
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">LLM 提供商</h3>
            <RadioGroup value={llmProvider} onValueChange={setLlmProvider}>
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="gemini" id="provider-gemini" />
                  <Label htmlFor="provider-gemini" className="font-normal cursor-pointer">Gemini</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="deepseek" id="provider-deepseek" />
                  <Label htmlFor="provider-deepseek" className="font-normal cursor-pointer">DeepSeek</Label>
                </div>
              </div>
            </RadioGroup>
          </div>

          <div className="space-y-4">
            <h3 className="text-lg font-semibold">API Keys</h3>
            <div className="grid grid-cols-1 gap-4">
              <div className="space-y-2">
                <Label>Gemini API Key</Label>
                <Input
                  type="password"
                  value={geminiApiKey}
                  onChange={(e) => setGeminiApiKey(e.target.value)}
                  placeholder="输入 Gemini API Key"
                />
                <p className="text-xs text-neutral-400">
                  如显示 "***已配置***" 表示已有配置，留空表示不修改
                </p>
              </div>
              <div className="space-y-2">
                <Label>DeepSeek API Key</Label>
                <Input
                  type="password"
                  value={deepseekApiKey}
                  onChange={(e) => setDeepseekApiKey(e.target.value)}
                  placeholder="输入 DeepSeek API Key"
                />
                <p className="text-xs text-neutral-400">
                  如显示 "***已配置***" 表示已有配置，留空表示不修改
                </p>
              </div>
            </div>
          </div>

          <div className="flex gap-3">
            <Button onClick={handleSaveSettings} disabled={savingSettings}>
              <Save className="mr-2 h-4 w-4" />
              {savingSettings ? "保存中..." : "保存 API Keys"}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 命宫配置 */}
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl font-bold">命宫配置</CardTitle>
          <CardDescription>
            配置您的命盘信息，保存后将用于首页三维运势预测。配置将保存到 config/owner.yaml 文件。
          </CardDescription>
        </CardHeader>
        <CardContent className="grid gap-6">
          {cfgError && (
            <div className="rounded-lg bg-red-500/10 border border-red-500/20 p-4 text-sm text-red-500">
              读取配置失败：{cfgError}
            </div>
          )}

          {/* 基本信息 */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">基本信息</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>姓名（可选）</Label>
                <Input
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="请输入姓名"
                />
              </div>
              <div className="space-y-2">
                <Label>性别</Label>
                <RadioGroup value={gender} onValueChange={setGender}>
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="男" id="male" />
                      <Label htmlFor="male" className="font-normal cursor-pointer">男</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="女" id="female" />
                      <Label htmlFor="female" className="font-normal cursor-pointer">女</Label>
                    </div>
                  </div>
                </RadioGroup>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <Checkbox
                id="isTai"
                checked={isTai}
                onCheckedChange={(checked) => setIsTai(checked as boolean)}
              />
              <Label htmlFor="isTai" className="font-normal cursor-pointer">
                胎身命
              </Label>
            </div>

            <div className="space-y-2">
              <Label>当前所在城市（可选）</Label>
              <Input
                value={currentCity}
                onChange={(e) => setCurrentCity(e.target.value)}
                placeholder="如：北京市"
              />
            </div>
          </div>

          {/* 出生时间 */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">出生时间</h3>

            <RadioGroup value={isLunar ? "lunar" : "solar"} onValueChange={(v) => setIsLunar(v === "lunar")}>
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="solar" id="solar" />
                  <Label htmlFor="solar" className="font-normal cursor-pointer">公历</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="lunar" id="lunar" />
                  <Label htmlFor="lunar" className="font-normal cursor-pointer">农历</Label>
                </div>
              </div>
            </RadioGroup>

            {!isLunar ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>出生日期</Label>
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button variant="outline" className={cn("w-full justify-start text-left font-normal", !date && "text-muted-foreground")}>
                        <CalendarIcon className="mr-2 h-4 w-4" />
                        {date ? format(date, "yyyy年MM月dd日") : <span>选择日期</span>}
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0">
                      <Calendar
                        mode="single"
                        captionLayout="dropdown"
                        fromYear={1900}
                        toYear={new Date().getFullYear()}
                        selected={date}
                        onSelect={setDate}
                        initialFocus
                      />
                    </PopoverContent>
                  </Popover>
                </div>
                <div className="space-y-2">
                  <Label>出生时间</Label>
                  <Input type="time" step="1" value={time} onChange={(e) => setTime(e.target.value)} />
                </div>
              </div>
            ) : (
              <div className="grid grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label>农历年</Label>
                  <Input
                    type="number"
                    value={lunarYear}
                    onChange={(e) => setLunarYear(e.target.value)}
                    placeholder="如：2001"
                  />
                </div>
                <div className="space-y-2">
                  <Label>农历月</Label>
                  <Input
                    type="number"
                    value={lunarMonth}
                    onChange={(e) => setLunarMonth(e.target.value)}
                    placeholder="如：11"
                  />
                </div>
                <div className="space-y-2">
                  <Label>农历日</Label>
                  <Input
                    type="number"
                    value={lunarDay}
                    onChange={(e) => setLunarDay(e.target.value)}
                    placeholder="如：9"
                  />
                </div>
              </div>
            )}
          </div>

          {/* 出生地点 */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">出生地点</h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label>省份</Label>
                <Select value={province} onValueChange={handleProvinceChange}>
                  <SelectTrigger>
                    <SelectValue placeholder="选择省份" />
                  </SelectTrigger>
                  <SelectContent>
                    {regionData.map((p) => (
                      <SelectItem key={p.value} value={p.value}>
                        {p.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>城市</Label>
                <Select value={city} onValueChange={handleCityChange} disabled={!province}>
                  <SelectTrigger>
                    <SelectValue placeholder="选择城市" />
                  </SelectTrigger>
                  <SelectContent>
                    {cities.map((c) => (
                      <SelectItem key={c.value} value={c.value}>
                        {c.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>地区</Label>
                <Select value={area} onValueChange={setArea} disabled={!city}>
                  <SelectTrigger>
                    <SelectValue placeholder="选择地区" />
                  </SelectTrigger>
                  <SelectContent>
                    {areas.map((a) => (
                      <SelectItem key={a.value} value={a.value}>
                        {a.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>

          {/* 计算出的四柱（只读显示） */}
          {(year || month || day || hour) && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">四柱八字</h3>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="rounded-lg border border-neutral-800 bg-black/20 p-3 text-center">
                  <div className="text-xs text-neutral-400 mb-1">年柱</div>
                  <div className="text-lg font-semibold">{year || "-"}</div>
                </div>
                <div className="rounded-lg border border-neutral-800 bg-black/20 p-3 text-center">
                  <div className="text-xs text-neutral-400 mb-1">月柱</div>
                  <div className="text-lg font-semibold">{month || "-"}</div>
                </div>
                <div className="rounded-lg border border-neutral-800 bg-black/20 p-3 text-center">
                  <div className="text-xs text-neutral-400 mb-1">日柱</div>
                  <div className="text-lg font-semibold">{day || "-"}</div>
                </div>
                <div className="rounded-lg border border-neutral-800 bg-black/20 p-3 text-center">
                  <div className="text-xs text-neutral-400 mb-1">时柱</div>
                  <div className="text-lg font-semibold">{hour || "-"}</div>
                </div>
              </div>
            </div>
          )}

          {/* 操作按钮 */}
          <div className="flex gap-3">
            <Button onClick={calcBazi} disabled={loading} variant="outline">
              <RefreshCw className={cn("mr-2 h-4 w-4", loading && "animate-spin")} />
              {loading ? "计算中..." : "计算四柱"}
            </Button>
            <Button onClick={handleSave} disabled={saving}>
              <Save className="mr-2 h-4 w-4" />
              {saving ? "保存中..." : "保存配置"}
            </Button>
          </div>
        </CardContent>
      </Card>
    </main>
  );
}