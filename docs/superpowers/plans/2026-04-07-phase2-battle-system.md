# Phase 2: 战斗系统 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 实现回合制战斗系统，支持 ATB 行动条、技能、元素克制

**Architecture:** 战斗系统独立于地图系统，战斗场景 BattleScene 处理所有战斗逻辑

**Tech Stack:** Phaser 3, TypeScript

---

## 文件结构

```
src/
├── data/
│   ├── battle-data.ts      # 战斗配置数据
│   └── skills.ts           # 技能数据
├── entities/
│   ├── BattleEntity.ts    # 战斗实体基类
│   ├── Hero.ts             # 英雄角色
│   └── Enemy.ts            # 敌方单位
├── systems/
│   ├── BattleSystem.ts     # 战斗核心系统
│   ├── ATBSystem.ts        # ATB 行动条系统
│   ├── SkillSystem.ts      # 技能系统
│   └── DamageCalculator.ts # 伤害计算
└── scenes/
    └── BattleScene.ts      # 战斗场景
```

---

## Task 1: 战斗数据结构

**Files:**
- Create: `src/data/element.ts`
- Create: `src/data/skills.ts`
- Create: `src/data/battle-data.ts`

### Step 1: 创建 src/data/element.ts

```typescript
export type ElementType = 'fire' | 'wind' | 'earth' | 'water' | 'holy' | 'dark' | 'neutral';

export const ELEMENT_EFFECTIVENESS: Record<ElementType, ElementType | null> = {
  fire: 'wind',
  wind: 'earth',
  earth: 'water',
  water: 'fire',
  holy: 'dark',
  dark: 'holy',
  neutral: null,
};

export function getElementMultiplier(attackElement: ElementType, defenseElement: ElementType): number {
  if (ELEMENT_EFFECTIVENESS[attackElement] === defenseElement) {
    return 2.0; // 克制
  }
  if (ELEMENT_EFFECTIVENESS[defenseElement] === attackElement) {
    return 0.5; // 被克制
  }
  return 1.0; // 正常
}
```

### Step 2: 创建 src/data/skills.ts

```typescript
import { ElementType } from './element';

export type SkillType = 'attack' | 'heal' | 'buff' | 'debuff';

export interface SkillData {
  id: string;
  name: string;
  type: SkillType;
  mpCost: number;
  power: number; // 技能威力
  target: 'single' | 'all' | 'self';
  element?: ElementType;
  description: string;
}

export const SKILLS: SkillData[] = [
  {
    id: 'skill_attack',
    name: '攻击',
    type: 'attack',
    mpCost: 0,
    power: 100,
    target: 'single',
    description: '普通物理攻击',
  },
  {
    id: 'skill_fireball',
    name: '火球术',
    type: 'attack',
    mpCost: 10,
    power: 150,
    target: 'single',
    element: 'fire',
    description: '发射火球攻击敌人',
  },
  {
    id: 'skill_heal',
    name: '治疗',
    type: 'heal',
    mpCost: 15,
    power: 80,
    target: 'single',
    description: '恢复队友生命',
  },
  {
    id: 'skill_power_up',
    name: '强化',
    type: 'buff',
    mpCost: 10,
    power: 0,
    target: 'self',
    description: '提升自身攻击力',
  },
];

export function getSkillById(id: string): SkillData | undefined {
  return SKILLS.find(s => s.id === id);
}
```

### Step 3: 创建 src/data/battle-data.ts

```typescript
import { ElementType } from './element';

export interface BattleStats {
  maxHp: number;
  maxMp: number;
  attack: number;
  defense: number;
  agility: number;
}

export interface BattleEntityData {
  id: string;
  name: string;
  level: number;
  element: ElementType;
  stats: BattleStats;
  skills: string[];
}

export const TEST_HERO: BattleEntityData = {
  id: 'hero_1',
  name: '冒险者',
  level: 1,
  element: 'neutral',
  stats: {
    maxHp: 100,
    maxMp: 50,
    attack: 20,
    defense: 10,
    agility: 15,
  },
  skills: ['skill_attack', 'skill_fireball', 'skill_heal', 'skill_power_up'],
};

export const TEST_ENEMIES: BattleEntityData[] = [
  {
    id: 'enemy_slime',
    name: '史莱姆',
    level: 1,
    element: 'water',
    stats: {
      maxHp: 30,
      maxMp: 0,
      attack: 10,
      defense: 5,
      agility: 8,
    },
    skills: ['skill_attack'],
  },
  {
    id: 'enemy_goblin',
    name: '哥布林',
    level: 2,
    element: 'earth',
    stats: {
      maxHp: 50,
      maxMp: 10,
      attack: 15,
      defense: 8,
      agility: 12,
    },
    skills: ['skill_attack'],
  },
];
```

### Step 4: 提交

```bash
git add -A && git commit -m "feat: 添加战斗数据结构"
```

---

## Task 2: 战斗实体类

**Files:**
- Create: `src/entities/BattleEntity.ts`
- Create: `src/entities/Hero.ts`
- Create: `src/entities/Enemy.ts`

### Step 1: 创建 src/entities/BattleEntity.ts

```typescript
import Phaser from 'phaser';
import { BattleEntityData, BattleStats } from '../data/battle-data';
import { ElementType } from '../data/element';

export abstract class BattleEntity extends Phaser.GameObjects.Container {
  public id: string;
  public name: string;
  public level: number;
  public element: ElementType;
  public skills: string[];

  protected hp: number;
  protected maxHp: number;
  protected mp: number;
  protected maxMp: number;
  protected attack: number;
  protected defense: number;
  protected agility: number;

  protected hpBar!: Phaser.GameObjects.Graphics;
  protected mpBar!: Phaser.GameObjects.Graphics;
  protected nameText!: Phaser.GameObjects.Text;

  constructor(scene: Phaser.Scene, data: BattleEntityData, x: number, y: number) {
    super(scene, x, y);
    this.id = data.id;
    this.name = data.name;
    this.level = data.level;
    this.element = data.element;
    this.skills = data.skills;

    this.maxHp = data.stats.maxHp;
    this.hp = this.maxHp;
    this.maxMp = data.stats.maxMp;
    this.mp = this.maxMp;
    this.attack = data.stats.attack;
    this.defense = data.stats.defense;
    this.agility = data.stats.agility;

    this.createUI();
    scene.add.existing(this);
  }

  protected abstract createUI(): void;

  public takeDamage(damage: number): void {
    this.hp = Math.max(0, this.hp - damage);
    this.updateHPBar();
  }

  public heal(amount: number): void {
    this.hp = Math.min(this.maxHp, this.hp + amount);
    this.updateHPBar();
  }

  public useMP(amount: number): boolean {
    if (this.mp >= amount) {
      this.mp -= amount;
      this.updateMPBar();
      return true;
    }
    return false;
  }

  protected updateHPBar(): void {
    // 子类实现
  }

  protected updateMPBar(): void {
    // 子类实现
  }

  public isDead(): boolean {
    return this.hp <= 0;
  }

  public getATBValue(): number {
    return this.agility;
  }

  public abstract getSprite(): Phaser.GameObjects.Sprite;
}
```

### Step 2: 创建 src/entities/Hero.ts

```typescript
import Phaser from 'phaser';
import { BattleEntity } from './BattleEntity';
import { BattleEntityData } from '../data/battle-data';

export class Hero extends BattleEntity {
  private sprite!: Phaser.GameObjects.Sprite;

  constructor(scene: Phaser.Scene, data: BattleEntityData, x: number, y: number) {
    super(scene, data, x, y);
  }

  protected createUI(): void {
    // 名称
    this.nameText = this.scene.add.text(-30, -45, `${this.name} Lv${this.level}`, {
      fontSize: '12px',
      color: '#00ffff',
    });
    this.add(this.nameText);

    // HP 条背景
    const hpBg = this.scene.add.graphics();
    hpBg.fillStyle(0x000000);
    hpBg.fillRect(-30, -30, 60, 6);
    this.add(hpBg);

    // HP 条
    this.hpBar = this.scene.add.graphics();
    this.updateHPBar();
    this.add(this.hpBar);

    // MP 条背景
    const mpBg = this.scene.add.graphics();
    mpBg.fillStyle(0x000000);
    mpBg.fillRect(-30, -22, 60, 4);
    this.add(mpBg);

    // MP 条
    this.mpBar = this.scene.add.graphics();
    this.updateMPBar();
    this.add(this.mpBar);
  }

  protected updateHPBar(): void {
    this.hpBar.clear();
    const ratio = this.hp / this.maxHp;
    const color = ratio > 0.5 ? 0x00ff00 : ratio > 0.25 ? 0xffff00 : 0xff0000;
    this.hpBar.fillStyle(color);
    this.hpBar.fillRect(-30, -30, 60 * ratio);
  }

  protected updateMPBar(): void {
    this.mpBar.clear();
    const ratio = this.mp / this.maxMp;
    this.mpBar.fillStyle(0x0000ff);
    this.mpBar.fillRect(-30, -22, 60 * ratio);
  }

  public setSprite(texture: string): void {
    this.sprite = this.scene.add.sprite(0, 0, texture);
    this.sprite.setOrigin(0.5);
    this.add(this.sprite);
  }

  public getSprite(): Phaser.GameObjects.Sprite {
    return this.sprite;
  }
}
```

### Step 3: 创建 src/entities/Enemy.ts

```typescript
import Phaser from 'phaser';
import { BattleEntity } from './BattleEntity';
import { BattleEntityData } from '../data/battle-data';

export class Enemy extends BattleEntity {
  private sprite!: Phaser.GameObjects.Sprite;

  constructor(scene: Phaser.Scene, data: BattleEntityData, x: number, y: number) {
    super(scene, data, x, y);
  }

  protected createUI(): void {
    // 名称
    this.nameText = this.scene.add.text(-30, -45, `${this.name} Lv${this.level}`, {
      fontSize: '12px',
      color: '#ff6666',
    });
    this.add(this.nameText);

    // HP 条背景
    const hpBg = this.scene.add.graphics();
    hpBg.fillStyle(0x000000);
    hpBg.fillRect(-30, -30, 60, 6);
    this.add(hpBg);

    // HP 条
    this.hpBar = this.scene.add.graphics();
    this.updateHPBar();
    this.add(this.hpBar);

    // MP 条
    const mpBg = this.scene.add.graphics();
    mpBg.fillStyle(0x000000);
    mpBg.fillRect(-30, -22, 60, 4);
    this.add(mpBg);

    this.mpBar = this.scene.add.graphics();
    this.updateMPBar();
    this.add(this.mpBar);
  }

  protected updateHPBar(): void {
    this.hpBar.clear();
    const ratio = this.hp / this.maxHp;
    const color = ratio > 0.5 ? 0x00ff00 : ratio > 0.25 ? 0xffff00 : 0xff0000;
    this.hpBar.fillStyle(color);
    this.hpBar.fillRect(-30, -30, 60 * ratio);
  }

  protected updateMPBar(): void {
    this.mpBar.clear();
    const ratio = this.mp / this.maxMp;
    this.mpBar.fillStyle(0x0000ff);
    this.mpBar.fillRect(-30, -22, 60 * ratio);
  }

  public setSprite(texture: string): void {
    this.sprite = this.scene.add.sprite(0, 0, texture);
    this.sprite.setOrigin(0.5);
    this.sprite.setTint(0xff6666);
    this.add(this.sprite);
  }

  public getSprite(): Phaser.GameObjects.Sprite {
    return this.sprite;
  }
}
```

### Step 4: 提交

```bash
git add -A && git commit -m "feat: 添加战斗实体类"
```

---

## Task 3: ATB 行动条系统

**Files:**
- Create: `src/systems/ATBSystem.ts`

### Step 1: 创建 src/systems/ATBSystem.ts

```typescript
import { BattleEntity } from '../entities/BattleEntity';

export interface ATBEntry {
  entity: BattleEntity;
  currentValue: number;
}

export class ATBSystem {
  private entries: ATBEntry[] = [];
  private readonly MAX_ATB = 100;

  public addEntity(entity: BattleEntity): void {
    this.entries.push({
      entity,
      currentValue: 0,
    });
  }

  public update(delta: number): BattleEntity[] {
    const ready: BattleEntity[] = [];

    for (const entry of this.entries) {
      if (entry.entity.isDead()) continue;

      entry.currentValue += entry.entity.getATBValue() * (delta / 1000);

      if (entry.currentValue >= this.MAX_ATB) {
        ready.push(entry.entity);
        entry.currentValue = 0;
      }
    }

    return ready;
  }

  public removeEntity(entity: BattleEntity): void {
    this.entries = this.entries.filter(e => e.entity !== entity);
  }

  public getEntries(): ATBEntry[] {
    return this.entries;
  }

  public clear(): void {
    this.entries = [];
  }
}
```

### Step 2: 提交

```bash
git add -A && git commit -m "feat: 添加 ATB 行动条系统"
```

---

## Task 4: 伤害计算系统

**Files:**
- Create: `src/systems/DamageCalculator.ts`

### Step 1: 创建 src/systems/DamageCalculator.ts

```typescript
import { BattleEntity } from '../entities/BattleEntity';
import { ElementType, getElementMultiplier } from '../data/element';
import { SkillData } from '../data/skills';

export interface DamageResult {
  damage: number;
  isCritical: boolean;
  elementEffectiveness: number;
}

export class DamageCalculator {
  static calculate(
    attacker: BattleEntity,
    defender: BattleEntity,
    skill: SkillData
  ): DamageResult {
    let damage = 0;
    let isCritical = false;
    let elementEffectiveness = 1.0;

    if (skill.type === 'attack' && skill.power > 0) {
      // 获取元素克制
      const attackElement: ElementType = skill.element || 'neutral';
      elementEffectiveness = getElementMultiplier(attackElement, defender.element);

      // 基础伤害 = 攻击 × 技能威力 / 防御
      const baseDamage = attacker.attack * (skill.power / 100);
      damage = baseDamage * (100 / (100 + defender.defense));

      // 元素克制
      damage *= elementEffectiveness;

      // 暴击（10% 概率，1.5 倍）
      if (Math.random() < 0.1) {
        isCritical = true;
        damage *= 1.5;
      }

      // 取整
      damage = Math.floor(damage);
    }

    return { damage, isCritical, elementEffectiveness };
  }

  static calculateHeal(healer: BattleEntity, skill: SkillData): number {
    if (skill.type !== 'heal') return 0;
    return Math.floor(healer.maxHp * (skill.power / 100));
  }
}
```

### Step 2: 提交

```bash
git add -A && git commit -m "feat: 添加伤害计算系统"
```

---

## Task 5: 技能系统

**Files:**
- Create: `src/systems/SkillSystem.ts`

### Step 1: 创建 src/systems/SkillSystem.ts

```typescript
import { BattleEntity } from '../entities/BattleEntity';
import { SkillData, getSkillById } from '../data/skills';
import { DamageCalculator, DamageResult } from './DamageCalculator';

export interface SkillResult {
  success: boolean;
  message: string;
  damageResult?: DamageResult;
  healAmount?: number;
}

export class SkillSystem {
  static useSkill(
    caster: BattleEntity,
    target: BattleEntity,
    skillId: string
  ): SkillResult {
    const skill = getSkillById(skillId);
    if (!skill) {
      return { success: false, message: '技能不存在' };
    }

    // 检查 MP
    if (!caster.useMP(skill.mpCost)) {
      return { success: false, message: '魔力不足' };
    }

    // 执行技能效果
    switch (skill.type) {
      case 'attack':
        const damageResult = DamageCalculator.calculate(caster, target, skill);
        target.takeDamage(damageResult.damage);
        return {
          success: true,
          message: `${caster.name} 对 ${target.name} 造成了 ${damageResult.damage} 点伤害${damageResult.isCritical ? ' (暴击!)' : ''}`,
          damageResult,
        };

      case 'heal':
        const healAmount = DamageCalculator.calculateHeal(caster, skill);
        target.heal(healAmount);
        return {
          success: true,
          message: `${caster.name} 恢复了 ${target.name} ${healAmount} 点生命`,
          healAmount,
        };

      case 'buff':
        // 简化：只显示消息
        return {
          success: true,
          message: `${caster.name} 使用了 ${skill.name}！`,
        };

      default:
        return { success: false, message: '未知技能类型' };
    }
  }

  static getUsableSkills(entity: BattleEntity): SkillData[] {
    return entity.skills
      .map(id => getSkillById(id))
      .filter((s): s is SkillData => s !== undefined && s.mpCost <= entity.mp);
  }
}
```

### Step 2: 提交

```bash
git add -A && git commit -m "feat: 添加技能系统"
```

---

## Task 6: 战斗核心系统

**Files:**
- Create: `src/systems/BattleSystem.ts`

### Step 1: 创建 src/systems/BattleSystem.ts

```typescript
import Phaser from 'phaser';
import { BattleEntity } from '../entities/BattleEntity';
import { Hero } from '../entities/Hero';
import { Enemy } from '../entities/Enemy';
import { ATBSystem } from './ATBSystem';
import { SkillSystem, SkillResult } from './SkillSystem';
import { BattleEntityData } from '../data/battle-data';
import { SKILLS } from '../data/skills';

export type BattleState = 'waiting' | 'selecting_action' | 'selecting_target' | 'executing' | 'victory' | 'defeat';

export interface BattleCallbacks {
  onStateChange?: (state: BattleState) => void;
  onLog?: (message: string) => void;
  onActionReady?: (entity: BattleEntity, skills: any[]) => void;
  onBattleEnd?: (victory: boolean) => void;
}

export class BattleSystem {
  private scene: Phaser.Scene;
  private heroes: Hero[] = [];
  private enemies: Enemy[] = [];
  private atbSystem: ATBSystem;
  private callbacks: BattleCallbacks = {};
  private state: BattleState = 'waiting';
  private currentActor: BattleEntity | null = null;

  constructor(scene: Phaser.Scene) {
    this.scene = scene;
    this.atbSystem = new ATBSystem();
  }

  setCallbacks(callbacks: BattleCallbacks): void {
    this.callbacks = callbacks;
  }

  startBattle(heroData: BattleEntityData[], enemyData: BattleEntityData[]): void {
    this.state = 'waiting';
    this.heroes = [];
    this.enemies = [];
    this.atbSystem.clear();

    // 创建英雄
    let heroX = 150;
    for (const data of heroData) {
      const hero = new Hero(this.scene, data, heroX, 350);
      hero.setSprite('player');
      this.heroes.push(hero);
      this.atbSystem.addEntity(hero);
      heroX += 120;
    }

    // 创建敌人
    let enemyX = 550;
    for (const data of enemyData) {
      const enemy = new Enemy(this.scene, data, enemyX, 150);
      enemy.setSprite('player');
      this.enemies.push(enemy);
      this.atbSystem.addEntity(enemy);
      enemyX += 100;
    }

    this.log('战斗开始！');
  }

  update(delta: number): void {
    if (this.state === 'victory' || this.state === 'defeat') return;

    // 检查战斗结束
    if (this.checkBattleEnd()) return;

    // 更新 ATB
    const readyEntities = this.atbSystem.update(delta);

    if (readyEntities.length > 0 && this.state === 'waiting') {
      this.currentActor = readyEntities[0];
      this.onActorReady(this.currentActor);
    }
  }

  private onActorReady(entity: BattleEntity): void {
    this.state = 'selecting_action';
    this.callbacks.onStateChange?.(this.state);

    const usableSkills = entity.skills
      .map(id => SKILLS.find(s => s.id === id))
      .filter(s => s !== undefined && entity.mp >= (s?.mpCost || 0));

    this.callbacks.onActionReady?.(entity, usableSkills);
  }

  executeAction(skillId: string, targetId: string): void {
    if (!this.currentActor) return;

    this.state = 'executing';
    const target = [...this.heroes, ...this.enemies].find(e => e.id === targetId);
    if (!target) return;

    const result = SkillSystem.useSkill(this.currentActor, target, skillId);
    this.log(result.message);

    this.checkBattleEnd();
  }

  endTurn(): void {
    this.currentActor = null;
    this.state = 'waiting';
    this.callbacks.onStateChange?.(this.state);
  }

  private checkBattleEnd(): boolean {
    const allEnemiesDead = this.enemies.every(e => e.isDead());
    const allHeroesDead = this.heroes.every(h => h.isDead());

    if (allEnemiesDead) {
      this.state = 'victory';
      this.log('胜利！');
      this.callbacks.onBattleEnd?.(true);
      return true;
    }

    if (allHeroesDead) {
      this.state = 'defeat';
      this.log('失败...');
      this.callbacks.onBattleEnd?.(false);
      return true;
    }

    return false;
  }

  private log(message: string): void {
    this.callbacks.onLog?.(message);
  }

  getState(): BattleState {
    return this.state;
  }

  getHeroes(): Hero[] {
    return this.heroes;
  }

  getEnemies(): Enemy[] {
    return this.enemies;
  }
}
```

### Step 2: 提交

```bash
git add -A && git commit -m "feat: 添加战斗核心系统"
```

---

## Task 7: 战斗场景

**Files:**
- Create: `src/scenes/BattleScene.ts`
- Modify: `src/scenes/UIScene.ts`

### Step 1: 创建 src/scenes/BattleScene.ts

```typescript
import Phaser from 'phaser';
import { BattleSystem, BattleState } from '../systems/BattleSystem';
import { TEST_HERO } from '../data/battle-data';
import { TEST_ENEMIES } from '../data/battle-data';
import { SkillData } from '../data/skills';

export class BattleScene extends Phaser.Scene {
  private battleSystem!: BattleSystem;
  private logText!: Phaser.GameObjects.Text;
  private skillButtons: Phaser.GameObjects.Text[] = [];
  private targetButtons: Phaser.GameObjects.Text[] = [];
  private currentSkills: SkillData[] = [];
  private currentActorId: string = '';

  constructor() {
    super({ key: 'BattleScene' });
  }

  create(): void {
    this.battleSystem = new BattleSystem(this);
    this.battleSystem.setCallbacks({
      onStateChange: (state) => this.onStateChange(state),
      onLog: (message) => this.onLog(message),
      onActionReady: (entity, skills) => this.onActionReady(entity, skills),
      onBattleEnd: (victory) => this.onBattleEnd(victory),
    });

    // 背景
    this.cameras.main.setBackgroundColor(0x2a2a4a);

    // 创建战斗日志区域
    this.logText = this.add.text(20, 450, '战斗开始！', {
      fontSize: '16px',
      color: '#ffffff',
      wordWrap: { width: 760 },
    });

    // 返回按钮
    const returnBtn = this.add.text(700, 10, '[ 返回 ]', {
      fontSize: '14px',
      color: '#aaaaaa',
    }).setInteractive();
    returnBtn.on('pointerdown', () => {
      this.scene.start('MapScene');
    });

    // 开始战斗
    this.battleSystem.startBattle([TEST_HERO], TEST_ENEMIES);
  }

  update(time: number, delta: number): void {
    this.battleSystem.update(delta);
  }

  private onStateChange(state: BattleState): void {
    this.clearButtons();

    if (state === 'victory') {
      this.showVictory();
    } else if (state === 'defeat') {
      this.showDefeat();
    }
  }

  private onLog(message: string): void {
    this.logText.setText(message);
  }

  private onActionReady(entity: any, skills: SkillData[]): void {
    this.currentActorId = entity.id;
    this.currentSkills = skills;

    this.add.text(20, 400, '选择技能:', {
      fontSize: '14px',
      color: '#ffff00',
    });

    let y = 420;
    for (let i = 0; i < skills.length; i++) {
      const skill = skills[i];
      const btn = this.add.text(40, y, `[${skill.name}] MP:${skill.mpCost}`, {
        fontSize: '14px',
        color: '#00ffff',
      }).setInteractive({ useHandCursor: true });

      btn.on('pointerover', () => btn.setColor('#ffffff'));
      btn.on('pointerout', () => btn.setColor('#00ffff'));
      btn.on('pointerdown', () => this.selectSkill(i));

      this.skillButtons.push(btn);
      y += 25;
    }
  }

  private selectSkill(index: number): void {
    this.clearButtons();
    const skill = this.currentSkills[index];
    const isHero = this.currentActorId.startsWith('hero');

    this.add.text(20, 400, '选择目标:', {
      fontSize: '14px',
      color: '#ffff00',
    });

    const targets = isHero ? this.battleSystem.getEnemies() : this.battleSystem.getHeroes();
    let y = 420;

    for (const target of targets) {
      if (target.isDead()) continue;

      const btn = this.add.text(40, y, `[${target.name}] HP:${target.hp}/${target.maxHp}`, {
        fontSize: '14px',
        color: '#ff6666',
      }).setInteractive({ useHandCursor: true });

      btn.on('pointerover', () => btn.setColor('#ffffff'));
      btn.on('pointerout', () => btn.setColor('#ff6666'));
      btn.on('pointerdown', () => {
        this.battleSystem.executeAction(skill.id, target.id);
        setTimeout(() => this.battleSystem.endTurn(), 500);
      });

      this.targetButtons.push(btn);
      y += 25;
    }
  }

  private clearButtons(): void {
    this.skillButtons.forEach(b => b.destroy());
    this.skillButtons = [];
    this.targetButtons.forEach(b => b.destroy());
    this.targetButtons = [];
  }

  private showVictory(): void {
    this.add.text(400, 250, '胜利!', {
      fontSize: '48px',
      color: '#ffcc00',
    }).setOrigin(0.5);

    const btn = this.add.text(350, 320, '[ 返回地图 ]', {
      fontSize: '20px',
      color: '#00ffff',
    }).setOrigin(0.5).setInteractive();

    btn.on('pointerdown', () => this.scene.start('MapScene'));
  }

  private showDefeat(): void {
    this.add.text(400, 250, '失败...', {
      fontSize: '48px',
      color: '#ff6666',
    }).setOrigin(0.5);

    const btn = this.add.text(350, 320, '[ 返回地图 ]', {
      fontSize: '20px',
      color: '#00ffff',
    }).setOrigin(0.5).setInteractive();

    btn.on('pointerdown', () => this.scene.start('MapScene'));
  }
}
```

### Step 2: 修改 src/main.ts 添加 BattleScene

```typescript
import Phaser from 'phaser';
import { GAME_CONFIG } from './config/game-config';
import { BootScene } from './scenes/BootScene';
import { LoadingScene } from './scenes/LoadingScene';
import { MenuScene } from './scenes/MenuScene';
import { MapScene } from './scenes/MapScene';
import { BattleScene } from './scenes/BattleScene';
import { UIScene } from './scenes/UIScene';

const config: Phaser.Types.Core.GameConfig = {
  type: Phaser.AUTO,
  width: GAME_CONFIG.width,
  height: GAME_CONFIG.height,
  parent: 'game-container',
  pixelArt: true,
  scene: [BootScene, LoadingScene, MenuScene, MapScene, BattleScene, UIScene],
};

new Phaser.Game(config);
```

### Step 3: 修改 MapScene 添加战斗入口

```typescript
// 在地图上添加一个战斗触发区域
// 在 create() 中添加：
const battleTrigger = this.add.text(400, 300, '[ 遇敌 ]', {
  fontSize: '24px',
  color: '#ff0000',
}).setOrigin(0.5).setInteractive();

battleTrigger.on('pointerdown', () => {
  this.scene.start('BattleScene');
});
```

### Step 4: 提交

```bash
git add -A && git commit -m "feat: 添加战斗场景"
```

---

## Phase 2 验收标准

- [ ] 战斗场景可进入
- [ ] ATB 行动条运作
- [ ] 技能可使用
- [ ] 伤害计算正确（含元素克制）
- [ ] 胜负判定正确

---

## 执行方式

**Two execution options:**

**1. Subagent-Driven (recommended)** - 每个 Task 分派独立子代理

**2. Inline Execution** - 在当前会话执行

**Which approach?**
