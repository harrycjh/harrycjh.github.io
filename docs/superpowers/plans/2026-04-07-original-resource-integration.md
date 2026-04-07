# 原版资源整合 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development

**Goal:** 整合原版资源，使用调色板着色，实现法兰城原版地图显示

**Architecture:**
- 解析原版 MAP 文件获取地图元数据
- 使用调色板 (.cgp) 为程序化瓦片着色
- 创建原版瓦片渲染器
- 扩展 FieldMap 支持原版地图

**Tech Stack:** Phaser 3, TypeScript, Node.js (资源解析工具)

---

## Task 1: 解析工具

**Files:**
- Create: `tools/parse-map.js`
- Create: `tools/parse-palette.js`

### Step 1: 创建地图解析工具

创建 `tools/parse-map.js`：

```javascript
const fs = require('fs');
const path = require('path');

const MAP_DIR = path.join(__dirname, '../Downloads/crossgate602/map/0');

function parseMapHeader(buffer) {
  const magic = buffer.slice(0, 3).toString();
  if (magic !== 'MAP') {
    throw new Error('Invalid MAP file: ' + magic);
  }

  // Little-endian parsing
  const version = buffer.readUInt32LE(4);
  const width = buffer.readUInt32LE(8);
  const height = buffer.readUInt32LE(12);
  const tileSize = buffer.readUInt32LE(16) || 32;

  return {
    magic,
    version,
    width,
    height,
    tileSize,
  };
}

function parseMapTileData(buffer, offset, width, height) {
  const tiles = [];
  let idx = offset;

  for (let y = 0; y < height; y++) {
    const row = [];
    for (let x = 0; x < width; x++) {
      if (idx + 4 <= buffer.length) {
        const tileId = buffer.readUInt32LE(idx);
        row.push(tileId);
        idx += 4;
      } else {
        row.push(0);
      }
    }
    tiles.push(row);
  }

  return tiles;
}

function parseMapFile(filename) {
  const filePath = path.join(MAP_DIR, filename);
  const buffer = fs.readFileSync(filePath);

  try {
    const header = parseMapHeader(buffer);
    const dataOffset = 1024; // Assuming 1024 byte header
    const tiles = parseMapTileData(buffer, dataOffset, header.width, header.height);

    return {
      id: filename.replace('.dat', ''),
      ...header,
      tiles,
      size: buffer.length,
    };
  } catch (e) {
    console.error(`Error parsing ${filename}: ${e.message}`);
    return null;
  }
}

function scanAllMaps() {
  const files = fs.readdirSync(MAP_DIR).filter(f => f.endsWith('.dat'));
  const maps = [];

  for (const file of files) {
    const map = parseMapFile(file);
    if (map) {
      maps.push(map);
    }
  }

  return maps;
}

// CLI
const args = process.argv.slice(2);
if (args[0] === '--scan') {
  const maps = scanAllMaps();
  console.log(JSON.stringify(maps, null, 2));
} else if (args[0]) {
  const map = parseMapFile(args[0]);
  console.log(JSON.stringify(map, null, 2));
}

module.exports = { parseMapFile, parseMapHeader, scanAllMaps };
```

### Step 2: 创建调色板解析工具

创建 `tools/parse-palette.js`：

```javascript
const fs = require('fs');
const path = require('path');

const PAL_DIR = path.join(__dirname, '../Downloads/crossgate602/bin/pal');

function parsePalette(filename) {
  const filePath = path.join(PAL_DIR, filename);
  const buffer = fs.readFileSync(filePath);

  if (buffer.length !== 708) {
    throw new Error(`Invalid palette file: ${buffer.length} bytes`);
  }

  const colors = [];
  for (let i = 0; i < 256; i++) {
    const offset = i * 3;
    colors.push({
      r: buffer[offset],
      g: buffer[offset + 1],
      b: buffer[offset + 2],
    });
  }

  return {
    name: filename.replace('.cgp', ''),
    colors,
  };
}

function parseAllPalettes() {
  const files = fs.readdirSync(PAL_DIR).filter(f => f.endsWith('.cgp'));
  const palettes = {};

  for (const file of files) {
    const palette = parsePalette(file);
    palettes[palette.name] = palette;
  }

  return palettes;
}

// Convert palette to CSS/Phaser format
function paletteToHexArray(palette) {
  return palette.colors.map(c =>
    (c.r << 16) | (c.g << 8) | c.b
  );
}

const args = process.argv.slice(2);
if (args[0] === '--all') {
  const palettes = parseAllPalettes();
  console.log(JSON.stringify(palettes, null, 2));
} else if (args[0]) {
  const palette = parsePalette(args[0]);
  console.log(JSON.stringify(palette, null, 2));
}

module.exports = { parsePalette, parseAllPalettes, paletteToHexArray };
```

### Step 3: 运行解析获取地图信息

```bash
node tools/parse-map.js --scan > src/data/original-maps-parsed.json
node tools/parse-palette.js --all > src/data/palettes.json
```

### Step 4: 提交

```bash
git add -A && git commit -m "feat: 添加原版资源解析工具"
```

---

## Task 2: 调色板系统

**Files:**
- Create: `src/systems/PaletteSystem.ts`
- Create: `src/data/palettes.ts`

### Step 1: 创建调色板数据

创建 `src/data/palettes.ts`：

```typescript
// 从 tools/parse-palette.js 生成的调色板数据
// 每个调色板 256 色 (RGB)

export interface PaletteColor {
  r: number;
  g: number;
  b: number;
}

export interface Palette {
  name: string;
  colors: PaletteColor[];
}

// 基础调色板 (从 palet_00.cgp)
export const PALETTE_00: Palette = {
  name: 'palet_00',
  colors: [
    { r: 133, g: 247, b: 246 },  // 0x85f7a4
    // ... 255 more colors
  ],
};

// 将 RGB 转换为 Phaser 十六进制颜色
export function rgbToHex(r: number, g: number, b: number): number {
  return (r << 16) | (g << 8) | b;
}

export function paletteToHexArray(palette: Palette): number[] {
  return palette.colors.map(c => rgbToHex(c.r, c.g, c.b));
}
```

### Step 2: 创建调色板系统

创建 `src/systems/PaletteSystem.ts`：

```typescript
import { PALETTE_00, paletteToHexArray, Palette } from '../data/palettes';

export class PaletteSystem {
  private currentPalette: number[];
  private palettes: Map<string, number[]> = new Map();

  constructor() {
    // 默认使用调色板 00
    this.currentPalette = paletteToHexArray(PALETTE_00);
    this.palettes.set('default', this.currentPalette);
  }

  getColor(index: number): number {
    if (index < 0 || index >= this.currentPalette.length) {
      return 0x000000;
    }
    return this.currentPalette[index];
  }

  getColorRGB(index: number): { r: number; g: number; b: number } | null {
    if (index < 0 || index >= this.currentPalette.length) {
      return null;
    }
    const hex = this.currentPalette[index];
    return {
      r: (hex >> 16) & 0xff,
      g: (hex >> 8) & 0xff,
      b: hex & 0xff,
    };
  }

  setPalette(paletteName: string): void {
    const palette = this.palettes.get(paletteName);
    if (palette) {
      this.currentPalette = palette;
    }
  }

  addPalette(name: string, colors: number[]): void {
    this.palettes.set(name, colors);
  }

  getCurrentPalette(): number[] {
    return this.currentPalette;
  }
}
```

### Step 3: 提交

```bash
git add -A && git commit -m "feat: 添加调色板系统"
```

---

## Task 3: 原版地图渲染器

**Files:**
- Modify: `src/systems/FieldMap.ts`

### Step 1: 扩展 FieldMap 支持原版地图

修改 `src/systems/FieldMap.ts` 添加原版瓦片渲染：

```typescript
import Phaser from 'phaser';
import { GAME_CONFIG } from '../config/game-config';
import { MapData, Building, Portal } from '../data/map-data';
import { PARIS_BUILDINGS, PARIS_PORTALS } from '../data/paris-buildings';
import { PaletteSystem } from './PaletteSystem';

// 原版地图元数据接口
export interface OriginalMapInfo {
  id: string;
  name: string;
  width: number;
  height: number;
  tileSize: number;
  type: 'town' | 'field' | 'dungeon';
  tileIds?: number[][]; // 原始瓦片数据
}

export class FieldMap {
  private scene: Phaser.Scene;
  private mapData: MapData;
  private originalMap?: OriginalMapInfo;
  private graphics!: Phaser.GameObjects.Graphics;
  private paletteSystem: PaletteSystem;
  // ... existing properties

  constructor(scene: Phaser.Scene, mapData: MapData, originalMap?: OriginalMapInfo) {
    this.scene = scene;
    this.mapData = mapData;
    this.originalMap = originalMap;
    this.paletteSystem = new PaletteSystem();
  }

  render(): void {
    if (this.originalMap?.tileIds) {
      this.renderOriginalTiles();
    } else {
      this.renderProcedural();
    }
    // ... rest of existing rendering
  }

  private renderOriginalTiles(): void {
    if (!this.originalMap?.tileIds) return;

    this.graphics = this.scene.add.graphics();
    const tiles = this.originalMap.tileIds;

    for (let y = 0; y < tiles.length; y++) {
      for (let x = 0; x < tiles[y].length; x++) {
        const tileId = tiles[y][x];
        this.renderTile(tileId, x, y);
      }
    }
  }

  private renderTile(tileId: number, x: number, y: number): void {
    const size = GAME_CONFIG.tileSize;
    const px = x * size;
    const py = y * size;

    // 使用调色板颜色作为占位符
    // 实际原版渲染需要 Graphic.bin 解析
    const color = this.paletteSystem.getColor(tileId % 256);

    this.graphics.fillStyle(color);
    this.graphics.fillRect(px, py, size, size);

    // 添加简单网格效果区分不同瓦片
    if (tileId !== 0) {
      this.graphics.lineStyle(1, 0x000000, 0.1);
      this.graphics.strokeRect(px, py, size, size);
    }
  }

  private renderProcedural(): void {
    // 现有的程序化渲染逻辑
    // ... existing code
  }
}
```

### Step 2: 提交

```bash
git add -A && git commit -m "feat: 添加原版地图渲染支持"
```

---

## Task 4: 法兰城原版地图

**Files:**
- Modify: `src/data/original-maps.ts`
- Create: `src/data/paris-original.ts`

### Step 1: 更新原版地图元数据

修改 `src/data/original-maps.ts`：

```typescript
export interface OriginalMapMeta {
  id: string;
  name: string;
  type: 'town' | 'field' | 'dungeon';
  BGM?: string;
  monsters?: string[];
  // 原版地图文件信息
  originalWidth?: number;
  originalHeight?: number;
}

// 法兰城地区地图 (ID 1000-1999)
export const PARIS_REGION_MAPS: OriginalMapMeta[] = [
  { id: '1000', name: '法兰城', type: 'town', originalWidth: 100, originalHeight: 100 },
  { id: '1001', name: '城东地区', type: 'field', monsters: ['slime_green', 'goblin'] },
  { id: '1002', name: '城西地区', type: 'field', monsters: ['bat', 'wolf'] },
  { id: '1003', name: '城南地区', type: 'field', monsters: ['slime_green'] },
  { id: '1004', name: '城北地区', type: 'field', monsters: ['goblin', 'bat'] },
  // 森林地区 (ID 2000-2999)
  { id: '2000', name: '伊尔森林', type: 'field', monsters: ['slime_green', 'goblin', 'bat', 'wolf'] },
  { id: '2001', name: '森林深处', type: 'dungeon', monsters: ['goblin', 'wolf'] },
  // 沙漠地区 (ID 3000-3999)
  { id: '3000', name: '沙漠地区', type: 'field', monsters: ['scorpion', 'sand_worm', 'mantis'] },
  // 雪原地区 (ID 4000-4999)
  { id: '4000', name: '雪拉伊雪原', type: 'field', monsters: ['ice_blob', 'snowman', 'bat'] },
  // 火山地区 (ID 5000-5999)
  { id: '5000', name: '火山地区', type: 'field', monsters: ['fire_spirit', 'lava_golem', 'wolf'] },
];

export function getMapById(id: string): OriginalMapMeta | undefined {
  return PARIS_REGION_MAPS.find(m => m.id === id);
}
```

### Step 2: 创建法兰城原版配置

创建 `src/data/paris-original.ts`：

```typescript
import { OriginalMapInfo } from '../systems/FieldMap';

// 法兰城主城原版地图信息
// 尺寸: 100x100 瓦片, 瓦片大小 32px
export const PARIS_ORIGINAL_MAP: OriginalMapInfo = {
  id: '1000',
  name: '法兰城',
  width: 100,
  height: 100,
  tileSize: 32,
  type: 'town',
};

// 传送点位置 (瓦片坐标)
export const PARIS_ORIGINAL_PORTALS = [
  { id: 'gate_east', x: 50, y: 1, targetMap: '2000', targetX: 50, targetY: 99 },
  { id: 'gate_west', x: 1, y: 50, targetMap: '3000', targetX: 99, targetY: 50 },
  { id: 'gate_south', x: 50, y: 99, targetMap: '4000', targetX: 50, targetY: 1 },
  { id: 'gate_north', x: 50, y: 1, targetMap: '5000', targetX: 50, targetY: 99 },
];

// 建筑物位置 (瓦片坐标)
export const PARIS_ORIGINAL_BUILDINGS = [
  { id: 'hospital', name: '医院', x: 35, y: 25, width: 8, height: 6 },
  { id: 'bank', name: '银行', x: 55, y: 25, width: 8, height: 6 },
  { id: 'weapon_shop', name: '武器店', x: 20, y: 50, width: 6, height: 6 },
  { id: 'magic_shop', name: '魔法店', x: 35, y: 50, width: 6, height: 6 },
  { id: 'inn', name: '旅馆', x: 70, y: 50, width: 6, height: 6 },
  { id: 'guild', name: '职业工会', x: 80, y: 35, width: 8, height: 8 },
  { id: 'pet_shop', name: '宠物店', x: 50, y: 75, width: 6, height: 6 },
];
```

### Step 3: 提交

```bash
git add -A && git commit -m "feat: 添加法兰城原版地图配置"
```

---

## Task 5: 资源加载器

**Files:**
- Create: `src/systems/ResourceLoader.ts`

### Step 1: 创建资源加载器

创建 `src/systems/ResourceLoader.ts`：

```typescript
import { OriginalMapInfo } from './FieldMap';

const ORIGINAL_RESOURCE_PATH = 'resources/crossgate602/';

export class ResourceLoader {
  private static instance: ResourceLoader;
  private mapCache: Map<string, OriginalMapInfo> = new Map();

  static getInstance(): ResourceLoader {
    if (!ResourceLoader.instance) {
      ResourceLoader.instance = new ResourceLoader();
    }
    return ResourceLoader.instance;
  }

  // 加载原版地图数据 (通过 fetch 从本地服务器)
  async loadOriginalMap(mapId: string): Promise<OriginalMapInfo | null> {
    if (this.mapCache.has(mapId)) {
      return this.mapCache.get(mapId)!;
    }

    try {
      const response = await fetch(`${ORIGINAL_RESOURCE_PATH}maps/${mapId}.json`);
      if (!response.ok) {
        return null;
      }
      const mapData = await response.json();
      this.mapCache.set(mapId, mapData);
      return mapData;
    } catch (e) {
      console.warn(`Failed to load original map ${mapId}:`, e);
      return null;
    }
  }

  // 预加载多个地图
  async preloadMaps(mapIds: string[]): Promise<void> {
    await Promise.all(mapIds.map(id => this.loadOriginalMap(id)));
  }

  // 获取调色板路径
  getPalettePath(paletteName: string = 'palet_00'): string {
    return `${ORIGINAL_RESOURCE_PATH}pal/${paletteName}.cgp`;
  }

  // 获取 BGM 路径
  getBGMPath(bgmName: string): string {
    return `${ORIGINAL_RESOURCE_PATH}bgm/${bgmName}.wav`;
  }

  // 获取音效路径
  getSEPath(seName: string): string {
    return `${ORIGINAL_RESOURCE_PATH}se/${seName}.wav`;
  }
}
```

### Step 2: 提交

```bash
git add -A && git commit -m "feat: 添加资源加载器"
```

---

## Task 6: 集成到游戏

**Files:**
- Modify: `src/scenes/MapScene.ts`

### Step 1: 更新 MapScene 支持原版地图

修改 `MapScene.ts` 的 `getMapData` 方法：

```typescript
import { ResourceLoader } from '../systems/ResourceLoader';
import { PARIS_ORIGINAL_MAP, PARIS_ORIGINAL_PORTALS, PARIS_ORIGINAL_BUILDINGS } from '../data/paris-original';

export class MapScene extends Phaser.Scene {
  // ... existing code

  private async getMapData(mapId: string): Promise<MapData> {
    // 检查是否是原版地图
    const resourceLoader = ResourceLoader.getInstance();
    const originalMap = await resourceLoader.loadOriginalMap(mapId);

    if (originalMap) {
      // 转换为我们的 MapData 格式
      return {
        id: originalMap.id,
        name: originalMap.name,
        width: originalMap.width,
        height: originalMap.height,
        tileSize: originalMap.tileSize,
        layers: [{ name: 'collision', width: originalMap.width, height: originalMap.height, data: [] }],
        groundColor: 0x8b7355, // 使用法兰城默认颜色
        portals: this.convertPortals(originalMap.id),
        buildings: this.convertBuildings(originalMap.id),
      };
    }

    // 回退到程序化地图
    if (mapId === 'paris') return PARIS_MAP;
    if (FIELD_MAPS[mapId]) return FIELD_MAPS[mapId];
    return PARIS_MAP;
  }

  private convertPortals(mapId: string): Portal[] {
    if (mapId === '1000') {
      return PARIS_ORIGINAL_PORTALS.map(p => ({
        ...p,
        radius: 30,
      }));
    }
    return [];
  }

  private convertBuildings(mapId: string): Building[] {
    if (mapId === '1000') {
      return PARIS_ORIGINAL_BUILDINGS.map(b => ({
        ...b,
        color: 0x8b7355,
      }));
    }
    return [];
  }
}
```

### Step 2: 提交

```bash
git add -A && git commit -m "feat: 集成原版资源到游戏"
```

---

## Task 7: 资源打包配置

**Files:**
- Create: `resources/crossgate602/.gitkeep`
- Modify: `.gitignore`

### Step 1: 添加资源目录占位符

```bash
mkdir -p resources/crossgate602/maps
mkdir -p resources/crossgate602/pal
mkdir -p resources/crossgate602/bgm
mkdir -p resources/crossgate602/se

# 复制调色板文件
cp ~/Downloads/crossgate602/bin/pal/*.cgp resources/crossgate602/pal/

touch resources/crossgate602/.gitkeep
```

### Step 2: 更新 .gitignore

```bash
# 添加到 .gitignore
resources/crossgate602/
!resources/crossgate602/.gitkeep
```

### Step 3: 提交

```bash
git add -A && git commit -m "feat: 添加原版资源配置"
```

---

## 验收标准

- [ ] 调色板文件可正确解析
- [ ] 地图元数据可正确解析（宽/高/名称）
- [ ] 法兰城原版地图配置完成
- [ ] FieldMap 支持原版地图瓦片渲染
- [ ] 资源加载器工作正常
- [ ] 游戏可加载原版地图数据

---

## 后续工作 (不包含在本计划内)

- 解析 Graphic_20.bin 提取精灵图
- 解析 Anime_*.bin 提取动画数据
- 实现完整的原版瓦片渲染
- 添加原版怪物/NPC 精灵

---

## 执行方式

**Subagent-Driven** - 每个 Task 分派独立子代理
