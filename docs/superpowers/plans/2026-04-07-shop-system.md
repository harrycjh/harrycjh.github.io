# 商店系统 实施计划

**Goal:** 实现商店系统，支持物品买卖、NPC 商店

---

## Task 1: 商店数据

**Files:**
- Create: `src/data/shop-data.ts`

### Step 1: 创建 src/data/shop-data.ts

```typescript
import { ItemData, ITEMS } from './item-data';

export interface ShopItem {
  itemId: string;
  price: number;
  stock: number; // -1 表示无限
}

export interface ShopData {
  id: string;
  name: string;
  items: ShopItem[];
}

export const SHOPS: Record<string, ShopData> = {
  potion_shop: {
    id: 'potion_shop',
    name: '治疗药水商店',
    items: [
      { itemId: 'potion', price: 50, stock: -1 },
      { itemId: 'hi_potion', price: 200, stock: -1 },
      { itemId: 'ether', price: 80, stock: -1 },
    ],
  },
  weapon_shop: {
    id: 'weapon_shop',
    name: '武器商店',
    items: [
      { itemId: 'iron_sword', price: 200, stock: 1 },
    ],
  },
  armor_shop: {
    id: 'armor_shop',
    name: '防具商店',
    items: [
      { itemId: 'leather_armor', price: 150, stock: 1 },
    ],
  },
};
```

### Step 2: 提交

```bash
git add -A && git commit -m "feat: 添加商店数据"
```

---

## Task 2: 商店系统

**Files:**
- Create: `src/systems/ShopSystem.ts`

### Step 1: 创建 src/systems/ShopSystem.ts

```typescript
import { ShopData, ShopItem, SHOPS } from '../data/shop-data';
import { InventorySystem } from './InventorySystem';

export class ShopSystem {
  private currentShop: ShopData | null = null;
  private inventory: InventorySystem;

  constructor(inventory: InventorySystem) {
    this.inventory = inventory;
  }

  openShop(shopId: string): ShopData | null {
    this.currentShop = SHOPS[shopId] || null;
    return this.currentShop;
  }

  buyItem(itemId: string, quantity: number = 1): boolean {
    if (!this.currentShop) return false;

    const shopItem = this.currentShop.items.find(i => i.itemId === itemId);
    if (!shopItem) return false;

    // 检查库存
    if (shopItem.stock !== -1 && shopItem.stock < quantity) return false;

    // 检查背包是否已满
    if (!this.inventory.addItem(itemId, quantity)) return false;

    // 扣除库存
    if (shopItem.stock !== -1) {
      shopItem.stock -= quantity;
    }

    return true;
  }

  sellItem(itemId: string, quantity: number = 1): boolean {
    if (!this.currentShop) return false;

    // 检查是否有物品可卖
    if (!this.inventory.hasItem(itemId)) return false;

    const itemData = this.inventory.getItemData(itemId);
    if (!itemData) return false;

    // 移除物品
    this.inventory.removeItem(itemId, quantity);

    // 获得金币（售价为原价的 50%）
    // 这里简化处理，实际应该有金币系统

    return true;
  }

  getCurrentShop(): ShopData | null {
    return this.currentShop;
  }
}
```

### Step 2: 提交

```bash
git add -A && git commit -m "feat: 添加商店系统"
```

---

## Task 3: 商店界面

**Files:**
- Create: `src/scenes/ShopScene.ts`

### Step 1: 创建 src/scenes/ShopScene.ts

```typescript
import Phaser from 'phaser';
import { ShopSystem } from '../systems/ShopSystem';
import { InventorySystem } from '../systems/InventorySystem';

export class ShopScene extends Phaser.Scene {
  private shopSystem!: ShopSystem;
  private inventory!: InventorySystem;
  private shopItems: Phaser.GameObjects.Container[] = [];
  private mode: 'buy' | 'sell' = 'buy';

  constructor() {
    super({ key: 'ShopScene' });
  }

  init(data: { shopId: string }): void {
    this.inventory = new InventorySystem();
    this.shopSystem = new ShopSystem(this.inventory);
    this.shopSystem.openShop(data.shopId);
  }

  create(): void {
    this.cameras.main.setBackgroundColor(0x1a1a2e);

    const shop = this.shopSystem.getCurrentShop();
    const shopName = shop?.name || '商店';

    this.add.text(400, 30, shopName, {
      fontSize: '24px',
      color: '#ffcc00',
    }).setOrigin(0.5);

    const backBtn = this.add.text(20, 20, '[ 返回 ]', {
      fontSize: '16px',
      color: '#aaaaaa',
    }).setInteractive();
    backBtn.on('pointerdown', () => this.scene.pop());

    // 购买/出售切换
    const buyBtn = this.add.text(300, 60, '[ 购买 ]', {
      fontSize: '16px',
      color: '#00ffff',
    }).setOrigin(0.5).setInteractive();
    buyBtn.on('pointerdown', () => {
      this.mode = 'buy';
      this.renderShopItems();
    });

    const sellBtn = this.add.text(500, 60, '[ 出售 ]', {
      fontSize: '16px',
      color: '#aaaaaa',
    }).setOrigin(0.5).setInteractive();
    sellBtn.on('pointerdown', () => {
      this.mode = 'sell';
      this.renderShopItems();
    });

    this.renderShopItems();
  }

  private renderShopItems(): void {
    this.shopItems.forEach(item => item.destroy());
    this.shopItems = [];

    const shop = this.shopSystem.getCurrentShop();
    if (!shop) return;

    let items: { itemId: string; price: number; stock: number; name: string }[] = [];

    if (this.mode === 'buy') {
      items = shop.items.map(shopItem => ({
        itemId: shopItem.itemId,
        price: shopItem.price,
        stock: shopItem.stock,
        name: this.inventory.getItemData(shopItem.itemId)?.name || shopItem.itemId,
      }));
    } else {
      const inv = this.inventory.getInventory();
      items = inv.map(slot => {
        const itemData = this.inventory.getItemData(slot.itemId);
        return {
          itemId: slot.itemId,
          price: Math.floor((itemData?.price || 0) * 0.5),
          stock: slot.quantity,
          name: itemData?.name || slot.itemId,
        };
      });
    }

    let y = 100;
    items.forEach((item, index) => {
      const container = this.add.container(100, y);

      const bg = this.add.graphics();
      bg.fillStyle(0x333366);
      bg.fillRect(0, 0, 600, 60);
      container.add(bg);

      const nameText = this.add.text(15, 10, item.name, {
        fontSize: '14px',
        color: '#00ffff',
      });
      container.add(nameText);

      const priceText = this.add.text(15, 32, `价格: ${item.price}`, {
        fontSize: '12px',
        color: '#ffcc00',
      });
      container.add(priceText);

      const stockText = this.add.text(400, 20, this.mode === 'buy' ? (item.stock === -1 ? '无限' : `库存: ${item.stock}`) : `拥有: ${item.stock}`, {
        fontSize: '12px',
        color: '#aaaaaa',
      });
      container.add(stockText);

      const actionBtn = this.add.text(500, 20, this.mode === 'buy' ? '[ 购买 ]' : '[ 出售 ]', {
        fontSize: '12px',
        color: '#00ff00',
      }).setInteractive();
      actionBtn.on('pointerdown', () => {
        if (this.mode === 'buy') {
          const success = this.shopSystem.buyItem(item.itemId);
          this.showMessage(success ? '购买成功！' : '购买失败！');
        } else {
          const success = this.shopSystem.sellItem(item.itemId);
          this.showMessage(success ? '出售成功！' : '出售失败！');
        }
        this.renderShopItems();
      });
      container.add(actionBtn);

      this.shopItems.push(container);
      y += 70;
    });
  }

  private showMessage(text: string): void {
    const msg = this.add.text(400, 550, text, {
      fontSize: '16px',
      color: '#ffffff',
    }).setOrigin(0.5);

    this.time.delayedCall(1000, () => msg.destroy());
  }
}
```

### Step 2: 提交

```bash
git add -A && git commit -m "feat: 添加商店界面"
```

---

## Task 4: 集成商店到 NPC

**Files:**
- Modify: `src/scenes/MapScene.ts`

### Step 1: 修改 NPC 对话添加商店入口

在 NPC 的 dialogs 中添加商店选项：

```typescript
const TEST_NPC: NPCData = {
  // ... existing dialogs
  dialogs: {
    shop: {
      text: '欢迎光临！需要买点什么吗？',
      choices: [
        { text: '购买药水', next: 'buy_potions' },
        { text: '离开', next: 'bye' },
      ],
    },
    buy_potions: {
      text: '请慢慢挑选~',
      action: 'open_shop:potion_shop',
    },
    // ... existing dialogs
  },
  // 修改 defaultDialog 为 'shop'
  defaultDialog: 'shop',
};
```

### Step 2: 提交

```bash
git add -A && git commit -m "feat: 集成商店到 NPC"
```

---

## 验收标准

- [ ] 商店数据完整
- [ ] 可以购买物品
- [ ] 可以出售物品
- [ ] NPC 对话可进入商店
