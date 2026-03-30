/**
 * 狼人杀联机游戏服务器
 * Node.js + WebSocket
 * 
 * 运行方式:
 *   1. npm install ws
 *   2. node server.js
 *   3. ngrok http 3000  (暴露到公网)
 */

const WebSocket = require('ws');
const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 3000;

// 创建 HTTP 服务器 (用于提供静态文件)
const server = http.createServer((req, res) => {
    const filePath = path.join(__dirname, 'werewolf.html');
    
    fs.readFile(filePath, (err, data) => {
        if (err) {
            res.writeHead(404);
            res.end('Not found');
            return;
        }
        res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
        res.end(data);
    });
});

// 创建 WebSocket 服务器
const wss = new WebSocket.Server({ server });

// 游戏状态
let games = new Map(); // gameId -> game state

// 角色定义
const ROLES = {
    WOLF: '狼人',
    VILLAGER: '村民',
    SEER: '预言家',
    WITCH: '女巫',
    HUNTER: '猎人',
    GUARD: '守卫',
    IDIOT: '白痴'
};

// 角色数量配置 (根据玩家数)
function getRoles(playerCount) {
    const configs = {
        6:  [ROLES.WOLF, ROLES.WOLF, ROLES.VILLAGER, ROLES.VILLAGER, ROLES.SEER, ROLES.WITCH],
        7:  [ROLES.WOLF, ROLES.WOLF, ROLES.VILLAGER, ROLES.VILLAGER, ROLES.VILLAGER, ROLES.SEER, ROLES.WITCH],
        8:  [ROLES.WOLF, ROLES.WOLF, ROLES.WOLF, ROLES.VILLAGER, ROLES.VILLAGER, ROLES.SEER, ROLES.WITCH, ROLES.HUNTER],
        9:  [ROLES.WOLF, ROLES.WOLF, ROLES.WOLF, ROLES.VILLAGER, ROLES.VILLAGER, ROLES.VILLAGER, ROLES.SEER, ROLES.WITCH, ROLES.HUNTER],
        10: [ROLES.WOLF, ROLES.WOLF, ROLES.WOLF, ROLES.VILLAGER, ROLES.VILLAGER, ROLES.VILLAGER, ROLES.SEER, ROLES.WITCH, ROLES.HUNTER, ROLES.GUARD],
        11: [ROLES.WOLF, ROLES.WOLF, ROLES.WOLF, ROLES.WOLF, ROLES.VILLAGER, ROLES.VILLAGER, ROLES.VILLAGER, ROLES.SEER, ROLES.WITCH, ROLES.HUNTER, ROLES.GUARD],
        12: [ROLES.WOLF, ROLES.WOLF, ROLES.WOLF, ROLES.WOLF, ROLES.VILLAGER, ROLES.VILLAGER, ROLES.VILLAGER, ROLES.VILLAGER, ROLES.SEER, ROLES.WITCH, ROLES.HUNTER, ROLES.GUARD]
    };
    return configs[playerCount] || configs[10];
}

// 游戏类
class WerewolfGame {
    constructor() {
        this.gameId = Date.now().toString(36);
        this.players = []; // { ws, name, role, alive, vote, usedPotion, usedPoison }
        this.phase = 'waiting';
        this.day = 0;
        this.currentAction = null;
        this.nightActions = {};
        this.message = '';
        this.winner = null;
    }
    
    addPlayer(ws, name) {
        if (this.phase !== 'waiting') return false;
        if (this.players.length >= 12) return false;
        
        const player = {
            ws,
            name,
            role: null,
            alive: true,
            vote: null,
            usedPotion: false,
            usedPoison: false,
            usedIdiot: false
        };
        this.players.push(player);
        // BUG FIX #1: 不在 addPlayer 里分配角色，只在 start() 时分配
        return true;
    }
    
    assignRoles() {
        const roleList = getRoles(this.players.length);
        // 打乱角色列表
        for (let i = roleList.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [roleList[i], roleList[j]] = [roleList[j], roleList[i]];
        }
        // 分配角色（不打乱玩家顺序，保留 playerIdx）
        // BUG FIX #2: 不再打乱 players 数组，避免 ws.playerIdx 错位
        for (let i = 0; i < this.players.length; i++) {
            this.players[i].role = roleList[i] || ROLES.VILLAGER;
        }
    }
    
    start() {
        if (this.players.length < 6) return false;
        this.assignRoles(); // BUG FIX #1: 只在这里分配角色
        this.phase = 'night';
        this.day = 1;
        this.nightActions = {};
        this.message = '天黑了，请闭眼...';
        this.broadcastState();
        this.executeNight();
        return true;
    }
    
    executeNight() {
        this.message = '第 ' + this.day + ' 天 - 狼人请睁眼';
        this.broadcastState();
        
        setTimeout(() => {
            this.currentAction = 'wolf_kill';
            this.message = '狼人请选择要击杀的目标';
            this.broadcastState();
        }, 3000);
    }
    
    handleNightAction(player, targetIdx, action) {
        if (this.phase !== 'night') return;
        
        switch (action) {
            case 'wolf_kill':
                if (player.role !== ROLES.WOLF || !player.alive) return;
                // BUG FIX #3: targetIdx 是玩家数组索引，直接存索引
                this.nightActions.wolfKill = targetIdx;
                this.message = '狼人已选择击杀目标';
                this.broadcastState();
                
                setTimeout(() => {
                    this.currentAction = 'witch_save';
                    this.message = '女巫，请选择是否使用解药';
                    this.broadcastState();
                }, 2000);
                break;
                
            case 'witch_save':
                if (player.role !== ROLES.WITCH || !player.alive) return;
                // BUG FIX #4: client 发 true/false，不再与 wolfKill 索引对比
                if (targetIdx === true && !player.usedPotion) {
                    this.nightActions.witchSave = true;
                    player.usedPotion = true;
                }
                this.message = '女巫选择完毕';
                this.broadcastState();
                
                setTimeout(() => {
                    this.currentAction = 'seer_check';
                    this.message = '预言家，请选择要查验的目标';
                    this.broadcastState();
                }, 2000);
                break;
                
            case 'seer_check':
                if (player.role !== ROLES.SEER || !player.alive) return;
                // BUG FIX #3: 用索引直接取玩家，不再用 find(p => p.ws === targetIdx)
                const target = this.players[targetIdx];
                if (target) {
                    const seerResult = {
                        player: player.name,
                        target: target.name,
                        role: target.role,
                        isWolf: target.role === ROLES.WOLF
                    };
                    this.nightActions.seerResult = seerResult;
                    // 只发给预言家本人
                    this.sendToPlayer(player, { type: 'seer_result', ...seerResult });
                }
                this.message = '预言家查验完毕';
                this.broadcastState();
                
                setTimeout(() => {
                    this.currentAction = 'guard_protect';
                    this.message = '守卫，请选择要守护的目标';
                    this.broadcastState();
                }, 2000);
                break;
                
            case 'guard_protect':
                if (player.role !== ROLES.GUARD || !player.alive) return;
                this.nightActions.guardTarget = targetIdx;
                this.message = '守卫守护完毕';
                this.broadcastState();
                
                setTimeout(() => this.dayBreak(), 2000);
                break;
        }
    }
    
    dayBreak() {
        this.phase = 'day';
        this.currentAction = null;
        
        const killedIdx = this.nightActions.wolfKill;
        let killedPlayer = null;
        
        if (killedIdx !== undefined) {
            // BUG FIX #5: 用索引直接取玩家
            const saved = this.nightActions.witchSave || this.nightActions.guardTarget === killedIdx;
            if (!saved) {
                killedPlayer = this.players[killedIdx];
                if (killedPlayer) {
                    killedPlayer.alive = false;
                }
            }
        }
        
        if (killedPlayer) {
            this.message = '昨夜 "' + killedPlayer.name + '" 倒下了，他的身份是 ' + killedPlayer.role;
        } else {
            this.message = '昨夜是平安夜，没有人死亡';
        }
        
        this.broadcastState();
        
        setTimeout(() => {
            if (this.checkWin()) return;
            
            this.phase = 'voting';
            this.message = '请大家投票选择要处决的玩家';
            this.currentAction = 'vote';
            this.players.forEach(p => p.vote = null);
            this.broadcastState();
        }, 5000);
    }
    
    handleVote(player, targetIdx) {
        if (this.phase !== 'voting') return;
        if (!player.alive) return;
        // 白痴：被票死后翻牌不死，但失去投票权
        if (player.role === ROLES.IDIOT && player.usedIdiot) return;
        
        player.vote = targetIdx;
        this.message = player.name + ' 投了票';
        this.broadcastState();
        
        const alivePlayers = this.players.filter(p => p.alive && !(p.role === ROLES.IDIOT && p.usedIdiot));
        if (alivePlayers.every(p => p.vote !== null)) {
            this.tallyVotes();
        }
    }
    
    tallyVotes() {
        const votes = {};
        const alivePlayers = this.players.filter(p => p.alive);
        
        alivePlayers.forEach(p => {
            if (p.vote !== null && p.vote !== undefined) {
                const key = p.vote;
                votes[key] = (votes[key] || 0) + 1;
            }
        });
        
        let maxVote = 0;
        let candidates = [];
        
        for (const [id, count] of Object.entries(votes)) {
            if (count > maxVote) {
                maxVote = count;
                candidates = [id];
            } else if (count === maxVote) {
                candidates.push(id);
            }
        }
        
        if (candidates.length === 1) {
            // BUG FIX #6: 用索引直接取玩家
            const eliminated = this.players[parseInt(candidates[0])];
            if (eliminated) {
                // 白痴特殊处理
                if (eliminated.role === ROLES.IDIOT && !eliminated.usedIdiot) {
                    eliminated.usedIdiot = true;
                    this.message = eliminated.name + ' 是白痴！翻牌不死，但失去投票权';
                } else {
                    eliminated.alive = false;
                    this.message = eliminated.name + ' 被投票出局，他的身份是 ' + eliminated.role;
                }
            }
        } else {
            this.message = '平票，无人出局';
        }
        
        this.broadcastState();
        
        setTimeout(() => {
            if (this.checkWin()) return;
            this.nextDay();
        }, 5000);
    }
    
    nextDay() {
        this.day++;
        this.phase = 'night';
        this.nightActions = {};
        this.message = '第 ' + this.day + ' 天 - 天黑了';
        this.broadcastState();
        
        setTimeout(() => this.executeNight(), 3000);
    }
    
    checkWin() {
        const wolves = this.players.filter(p => p.role === ROLES.WOLF && p.alive);
        const good = this.players.filter(p => p.role !== ROLES.WOLF && p.alive);
        
        if (wolves.length === 0) {
            this.winner = 'good';
            this.phase = 'ending';
            this.message = '游戏结束！好人胜利！';
            this.broadcastState();
            return true;
        }
        
        if (wolves.length >= good.length) {
            this.winner = 'wolf';
            this.phase = 'ending';
            this.message = '游戏结束！狼人胜利！';
            this.broadcastState();
            return true;
        }
        
        return false;
    }
    
    sendToPlayer(player, data) {
        if (player.ws.readyState === WebSocket.OPEN) {
            player.ws.send(JSON.stringify(data));
        }
    }
    
    broadcastState() {
        // BUG FIX #7: 每个玩家只看到自己的角色，其他人在游戏中角色隐藏
        // BUG FIX #8: 添加 nightKillName 供女巫 UI 使用
        this.players.forEach((me, myIdx) => {
            if (me.ws.readyState !== WebSocket.OPEN) return;
            
            // 计算女巫需要知道的被杀目标名字
            let nightKillName = null;
            if (this.currentAction === 'witch_save' && this.nightActions.wolfKill !== undefined) {
                const killed = this.players[this.nightActions.wolfKill];
                if (killed) nightKillName = killed.name;
            }
            
            const state = {
                type: 'game_state',
                gameId: this.gameId,
                phase: this.phase,
                day: this.day,
                message: this.message,
                winner: this.winner,
                currentAction: this.currentAction,
                nightKillName,
                players: this.players.map((p, i) => ({
                    id: i,
                    name: p.name,
                    // 只在结束时或是自己时才发角色；狼人可以看到队友
                    role: this.phase === 'ending'
                        ? p.role
                        : (i === myIdx || (me.role === ROLES.WOLF && p.role === ROLES.WOLF))
                            ? p.role
                            : null,
                    alive: p.alive,
                    isHost: i === 0,
                    vote: p.vote
                }))
            };
            
            me.ws.send(JSON.stringify(state));
        });
    }
    
    removePlayer(ws) {
        const idx = this.players.findIndex(p => p.ws === ws);
        if (idx !== -1) {
            this.players.splice(idx, 1);
            // 更新剩余玩家的 playerIdx
            this.players.forEach((p, i) => {
                p.ws.playerIdx = i;
            });
            
            if (this.phase === 'waiting' && this.players.length === 0) {
                games.delete(this.gameId);
            } else {
                this.broadcastState();
            }
        }
    }
}

// WebSocket 连接处理
wss.on('connection', (ws) => {
    console.log('新连接');
    
    ws.on('message', (data) => {
        try {
            const msg = JSON.parse(data);
            
            switch (msg.type) {
                case 'create_game': {
                    const game = new WerewolfGame();
                    games.set(game.gameId, game);
                    game.addPlayer(ws, msg.name);
                    ws.gameId = game.gameId;
                    ws.playerIdx = 0;
                    ws.send(JSON.stringify({
                        type: 'game_created',
                        gameId: game.gameId,
                        playerIdx: 0
                    }));
                    game.broadcastState();
                    break;
                }
                    
                case 'join_game': {
                    const g = games.get(msg.gameId);
                    if (g) {
                        if (g.addPlayer(ws, msg.name)) {
                            ws.gameId = msg.gameId;
                            ws.playerIdx = g.players.length - 1;
                            ws.send(JSON.stringify({
                                type: 'joined',
                                gameId: msg.gameId,
                                playerIdx: ws.playerIdx
                            }));
                            g.broadcastState();
                        } else {
                            ws.send(JSON.stringify({ type: 'error', message: '无法加入房间' }));
                        }
                    } else {
                        ws.send(JSON.stringify({ type: 'error', message: '房间不存在' }));
                    }
                    break;
                }
                    
                case 'start_game': {
                    const gameToStart = games.get(ws.gameId);
                    // 只有第一个玩家（房主，idx=0）才能开始
                    if (gameToStart && ws.playerIdx === 0) {
                        gameToStart.start();
                    }
                    break;
                }
                    
                case 'night_action': {
                    const gameForAction = games.get(ws.gameId);
                    if (gameForAction) {
                        const player = gameForAction.players[ws.playerIdx];
                        if (player) {
                            gameForAction.handleNightAction(player, msg.target, msg.action);
                        }
                    }
                    break;
                }
                    
                case 'vote': {
                    const gameForVote = games.get(ws.gameId);
                    if (gameForVote) {
                        const voter = gameForVote.players[ws.playerIdx];
                        if (voter) {
                            gameForVote.handleVote(voter, msg.target);
                        }
                    }
                    break;
                }
            }
        } catch (e) {
            console.error('消息解析错误:', e);
        }
    });
    
    ws.on('close', () => {
        const game = games.get(ws.gameId);
        if (game) {
            game.removePlayer(ws);
        }
    });
});

server.listen(PORT, () => {
    console.log(`
╔═══════════════════════════════════════════╗
║         🎭 狼人杀联机服务器已启动         ║
╠═══════════════════════════════════════════╣
║  本地地址: http://localhost:${PORT}          ║
║                                           ║
║  ⚠️  需要公网访问？运行:                  ║
║     ngrok http ${PORT}                     ║
║                                           ║
╚═══════════════════════════════════════════╝
    `);
});
