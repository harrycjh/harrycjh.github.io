# 职业系统 实施计划

**Goal:** 实现职业系统，不同职业有不同属性和技能

---

## Task 1: 职业数据

**Files:**
- Create: `src/data/job-data.ts`

### Step 1: 创建 src/data/job-data.ts

```typescript
import { ElementType } from './element';

export type JobId = 'swordsman' | 'magician' | 'knight' | 'archer';

export interface JobData {
  id: JobId;
  name: string;
  description: string;
  baseStats: {
    maxHp: number;
    maxMp: number;
    attack: number;
    defense: number;
    agility: number;
  };
  growthStats: {
    hpPerLevel: number;
    mpPerLevel: number;
    attackPerLevel: number;
    defensePerLevel: number;
    agilityPerLevel: number;
  };
  skills: string[];
  element: ElementType;
}

export const JOBS: Record<JobId, JobData> = {
  swordsman: {
    id: 'swordsman',
    name: '剑士',
    description: '物理攻击型职业，擅长近战',
    baseStats: {
      maxHp: 120,
      maxMp: 30,
      attack: 25,
      defense: 12,
      agility: 10,
    },
    growthStats: {
      hpPerLevel: 15,
      mpPerLevel: 3,
      attackPerLevel: 4,
      defensePerLevel: 2,
      agilityPerLevel: 1,
    },
    skills: ['skill_attack', 'skill_power_up', 'skill_heavy_strike'],
    element: 'neutral',
  },
  magician: {
    id: 'magician',
    name: '魔法师',
    description: '魔法攻击型职业，擅长元素魔法',
    baseStats: {
      maxHp: 70,
      maxMp: 80,
      attack: 8,
      defense: 5,
      agility: 12,
    },
    growthStats: {
      hpPerLevel: 8,
      mpPerLevel: 12,
      attackPerLevel: 1,
      defensePerLevel: 1,
      agilityPerLevel: 2,
    },
    skills: ['skill_attack', 'skill_fireball', 'skill_ice_arrow', 'skill_heal'],
    element: 'fire',
  },
  knight: {
    id: 'knight',
    name: '骑士',
    description: '防御型职业，擅长保护队友',
    baseStats: {
      maxHp: 100,
      maxMp: 40,
      attack: 18,
      defense: 18,
      agility: 8,
    },
    growthStats: {
      hpPerLevel: 12,
      mpPerLevel: 5,
      attackPerLevel: 2,
      defensePerLevel: 3,
      agilityPerLevel: 1,
    },
    skills: ['skill_attack', 'skill_guard', 'skill_charge'],
    element: 'earth',
  },
  archer: {
    id: 'archer',
    name: '弓箭手',
    description: '敏捷型职业，擅长远程攻击',
    baseStats: {
      maxHp: 90,
      maxMp: 35,
      attack: 20,
      defense: 8,
      agility: 18,
    },
    growthStats: {
      hpPerLevel: 10,
      mpPerLevel: 4,
      attackPerLevel: 3,
      defensePerLevel: 1,
      agilityPerLevel: 3,
    },
    skills: ['skill_attack', 'skill_double_shot', 'skill_poison_arrow'],
    element: 'wind',
  },
};

export function getJobById(id: JobId): JobData | undefined {
  return JOBS[id];
}
```

### Step 2: 添加新技能

修改 src/data/skills.ts 添加职业专属技能：

```typescript
{
  id: 'skill_heavy_strike',
  name: '重击',
  type: 'attack',
  mpCost: 15,
  power: 180,
  target: 'single',
  description: '造成大量物理伤害',
},
{
  id: 'skill_ice_arrow',
  name: '冰箭',
  type: 'attack',
  mpCost: 12,
  power: 120,
  target: 'single',
  element: 'water',
  description: '水属性魔法攻击',
},
{
  id: 'skill_guard',
  name: '防御',
  type: 'buff',
  mpCost: 10,
  power: 0,
  target: 'self',
  description: '提升自身防御力',
},
{
  id: 'skill_charge',
  name: '冲锋',
  type: 'attack',
  mpCost: 20,
  power: 150,
  target: 'single',
  description: '骑乘冲锋攻击',
},
{
  id: 'skill_double_shot',
  name: '双击',
  type: 'attack',
  mpCost: 15,
  power: 100,
  target: 'single',
  description: '连续攻击两次',
},
{
  id: 'skill_poison_arrow',
  name: '毒箭',
  type: 'attack',
  mpCost: 18,
  power: 90,
  target: 'single',
  element: 'earth',
  description: '附带中毒效果',
},
```

### Step 3: 提交

```bash
git add -A && git commit -m "feat: 添加职业系统数据"
```

---

## Task 2: 角色创建界面

**Files:**
- Create: `src/scenes/JobSelectScene.ts`

### Step 1: 创建 src/scenes/JobSelectScene.ts

```typescript
import Phaser from 'phaser';
import { JOBS, JobData, JobId } from '../data/job-data';

export class JobSelectScene extends Phaser.Scene {
  private jobCards: Phaser.GameObjects.Container[] = [];

  constructor() {
    super({ key: 'JobSelectScene' });
  }

  create(): void {
    this.cameras.main.setBackgroundColor(0x1a1a2e);

    this.add.text(400, 40, '选择职业', {
      fontSize: '32px',
      color: '#ffcc00',
    }).setOrigin(0.5);

    this.renderJobCards();
  }

  private renderJobCards(): void {
    const jobList = Object.values(JOBS);
    let x = 100;
    let y = 120;

    jobList.forEach((job) => {
      const card = this.createJobCard(job, x, y);
      this.jobCards.push(card);
      x += 200;
      if (x > 700) {
        x = 100;
        y += 200;
      }
    });
  }

  private createJobCard(job: JobData, x: number, y: number): Phaser.GameObjects.Container {
    const card = this.add.container(x, y);

    const bg = this.add.graphics();
    bg.fillStyle(0x333366);
    bg.fillRoundedRect(0, 0, 180, 180, 12);
    bg.lineStyle(2, 0x6666ff);
    bg.strokeRoundedRect(0, 0, 180, 180, 12);
    card.add(bg);

    const nameText = this.add.text(90, 20, job.name, {
      fontSize: '20px',
      color: '#ffcc00',
      fontStyle: 'bold',
    }).setOrigin(0.5);
    card.add(nameText);

    const descText = this.add.text(90, 50, job.description, {
      fontSize: '11px',
      color: '#aaaaaa',
      align: 'center',
    }).setOrigin(0.5);
    card.add(descText);

    const statsText = this.add.text(15, 80, [
      `HP: ${job.baseStats.maxHp}`,
      `MP: ${job.baseStats.maxMp}`,
      `攻击: ${job.baseStats.attack}`,
      `防御: ${job.baseStats.defense}`,
      `敏捷: ${job.baseStats.agility}`,
    ].join('\n'), {
      fontSize: '11px',
      color: '#ffffff',
    });
    card.add(statsText);

    const selectBtn = this.add.text(90, 160, '[ 选择 ]', {
      fontSize: '14px',
      color: '#00ff00',
    }).setOrigin(0.5).setInteractive();
    selectBtn.on('pointerover', () => selectBtn.setColor('#ffffff'));
    selectBtn.on('pointerout', () => selectBtn.setColor('#00ff00'));
    selectBtn.on('pointerdown', () => this.selectJob(job));
    card.add(selectBtn);

    return card;
  }

  private selectJob(job: JobData): void {
    // 保存选择的职业
    localStorage.setItem('selectedJob', JSON.stringify(job));

    // 跳转到主游戏
    this.scene.start('MapScene');
  }
}
```

### Step 2: 提交

```bash
git add -A && git commit -m "feat: 添加职业选择界面"
```

---

## Task 3: 集成职业到战斗

**Files:**
- Modify: `src/scenes/BattleScene.ts`

### Step 1: 修改战斗使用角色职业

修改 BattleScene 使用玩家选择的职业属性：

```typescript
// 在 create() 中获取职业数据
const savedJob = localStorage.getItem('selectedJob');
const jobData = savedJob ? JSON.parse(savedJob) : {
  id: 'swordsman',
  name: '剑士',
  stats: { maxHp: 120, maxMp: 30, attack: 25, defense: 12, agility: 10 },
  skills: ['skill_attack', 'skill_power_up', 'skill_heavy_strike'],
};

// 使用职业数据创建角色
const heroData: BattleEntityData = {
  id: 'hero_1',
  name: jobData.name,
  level: 1,
  element: 'neutral',
  stats: jobData.stats,
  skills: jobData.skills,
};
```

### Step 2: 提交

```bash
git add -A && git commit -m "feat: 集成职业到战斗系统"
```

---

## Task 4: 主菜单进入职业选择

**Files:**
- Modify: `src/scenes/MenuScene.ts`

### Step 1: 修改主菜单

```typescript
startBtn.on('pointerdown', () => {
  this.scene.start('JobSelectScene');
});
```

### Step 2: 提交

```bash
git add -A && git commit -m "feat: 主菜单进入职业选择"
```

---

## 验收标准

- [ ] 4 个职业可选（剑士、魔法师、骑士、弓箭手）
- [ ] 职业有不同属性和技能
- [ ] 职业选择界面显示职业信息
- [ ] 战斗中应用职业属性和技能
