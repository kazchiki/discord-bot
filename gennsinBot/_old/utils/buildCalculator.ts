const genshindb = require('genshin-db');

// レベル範囲と昇格段階のマッピング
const ASCENSION_LEVELS = {
    1: { minLevel: 1, maxLevel: 20 },
    2: { minLevel: 20, maxLevel: 40 },
    3: { minLevel: 40, maxLevel: 50 },
    4: { minLevel: 50, maxLevel: 60 },
    5: { minLevel: 60, maxLevel: 70 },
    6: { minLevel: 70, maxLevel: 80 },
    7: { minLevel: 80, maxLevel: 90 }
} as const;

// キャラクター経験値テーブル（レベル1→20、20→40など）
const EXP_REQUIREMENTS = {
    '1-20': 120175,
    '20-40': 578325,
    '40-50': 579100,
    '50-60': 854125,
    '60-70': 1195925,
    '70-80': 1611875,
    '80-90': 2421875
} as const;

interface BuildCost {
    mora: number;
    materials: Array<{
        name: string;
        count: number;
        rarity: number;
    }>;
    expBooks: {
        heroWit: number;
        adventurerExp: number;
        wandererAdvice: number;
    };
}

interface TalentCost {
    mora: number;
    materials: Array<{
        name: string;
        count: number;
        rarity: number;
    }>;
}

// 必要昇格段階を計算
function getRequiredAscensions(currentLevel: number, targetLevel: number): number[] {
    const requiredAscensions: number[] = [];
    
    for (let ascension = 1; ascension <= 6; ascension++) {
        const ascensionData = ASCENSION_LEVELS[ascension as keyof typeof ASCENSION_LEVELS];
        
        // 現在レベルがこの昇格段階より下で、目標レベルがこの昇格段階以上の場合
        if (currentLevel < ascensionData.maxLevel && targetLevel >= ascensionData.maxLevel) {
            requiredAscensions.push(ascension);
        }
    }
    
    return requiredAscensions;
}

// 経験値を経験書に変換
function convertExpToBooks(totalExp: number) {
    // Hero's Wit (紫本) = 20,000 EXP
    // Adventurer's Experience (青本) = 5,000 EXP  
    // Wanderer's Advice (緑本) = 1,000 EXP
    
    const heroWit = Math.floor(totalExp / 20000);
    let remainingExp = totalExp % 20000;
    
    const adventurerExp = Math.floor(remainingExp / 5000);
    remainingExp = remainingExp % 5000;
    
    const wandererAdvice = Math.ceil(remainingExp / 1000);
    
    return {
        heroWit,
        adventurerExp,
        wandererAdvice
    };
}

// レベル上げ必要経験値を計算
function calculateExpRequirement(currentLevel: number, targetLevel: number): number {
    let totalExp = 0;
    
    // 各段階の経験値を累積
    const stages = [
        { range: '1-20', min: 1, max: 20 },
        { range: '20-40', min: 20, max: 40 },
        { range: '40-50', min: 40, max: 50 },
        { range: '50-60', min: 50, max: 60 },
        { range: '60-70', min: 60, max: 70 },
        { range: '70-80', min: 70, max: 80 },
        { range: '80-90', min: 80, max: 90 }
    ];
    
    for (const stage of stages) {
        const stageStart = Math.max(stage.min, currentLevel);
        const stageEnd = Math.min(stage.max, targetLevel);
        
        if (stageStart < stageEnd) {
            const stageExp = EXP_REQUIREMENTS[stage.range as keyof typeof EXP_REQUIREMENTS];
            const progress = (stageEnd - stageStart) / (stage.max - stage.min);
            totalExp += Math.floor(stageExp * progress);
        }
    }
    
    return totalExp;
}

// キャラクター育成コスト計算
export async function calculateBuildCost(
    characterName: string,
    currentLevel: number,
    targetLevel: number
): Promise<BuildCost | null> {
    try {
        // 日本語結果を取得
        genshindb.setOptions({ resultLanguage: 'Japanese' });
        const character = genshindb.characters(characterName);
        
        if (!character) {
            return null;
        }
        
        const requiredAscensions = getRequiredAscensions(currentLevel, targetLevel);
        let totalMora = 0;
        const materialMap = new Map<string, { count: number; rarity: number }>();
        
        // 昇格コストを計算
        for (const ascension of requiredAscensions) {
            const ascensionKey = `ascend${ascension}` as keyof typeof character.costs;
            const costs = character.costs[ascensionKey];
            
            if (costs) {
                for (const cost of costs) {
                    if (cost.name === 'Mora') {
                        totalMora += cost.count;
                    } else {
                        const existing = materialMap.get(cost.name) || { count: 0, rarity: 1 };
                        materialMap.set(cost.name, {
                            count: existing.count + cost.count,
                            rarity: existing.rarity
                        });
                    }
                }
            }
        }
        
        // レベル上げ経験値コストを計算
        const expRequirement = calculateExpRequirement(currentLevel, targetLevel);
        const expBooks = convertExpToBooks(expRequirement);
        
        // レベル上げのモラコスト（経験書使用コスト）
        const expMoraCost = (expBooks.heroWit * 4000) + (expBooks.adventurerExp * 1000) + (expBooks.wandererAdvice * 200);
        totalMora += expMoraCost;
        
        // 素材配列に変換
        const materials = Array.from(materialMap.entries()).map(([name, data]) => ({
            name,
            count: data.count,
            rarity: data.rarity
        }));
        
        return {
            mora: totalMora,
            materials,
            expBooks
        };
        
    } catch (error) {
        console.error('育成コスト計算エラー:', error);
        return null;
    }
}

// 天賦育成コスト計算
export async function calculateTalentCost(
    characterName: string,
    talentType: 'normal' | 'skill' | 'burst',
    currentLevel: number,
    targetLevel: number
): Promise<TalentCost | null> {
    try {
        genshindb.setOptions({ resultLanguage: 'Japanese' });
        const talent = genshindb.talents(characterName);
        
        if (!talent || !talent.costs) {
            return null;
        }
        
        let totalMora = 0;
        const materialMap = new Map<string, { count: number; rarity: number }>();
        
        // 指定されたレベル範囲の天賦育成コストを計算
        for (let level = currentLevel; level < targetLevel; level++) {
            const costKey = `lvl${level + 1}` as keyof typeof talent.costs;
            const costs = talent.costs[costKey];
            
            if (costs) {
                for (const cost of costs) {
                    if (cost.name === 'Mora') {
                        totalMora += cost.count;
                    } else {
                        const existing = materialMap.get(cost.name) || { count: 0, rarity: 1 };
                        materialMap.set(cost.name, {
                            count: existing.count + cost.count,
                            rarity: existing.rarity
                        });
                    }
                }
            }
        }
        
        const materials = Array.from(materialMap.entries()).map(([name, data]) => ({
            name,
            count: data.count,
            rarity: data.rarity
        }));
        
        return {
            mora: totalMora,
            materials
        };
        
    } catch (error) {
        console.error('天賦コスト計算エラー:', error);
        return null;
    }
}

// 完全育成コスト計算（レベル90、天賦9/9/9）
export async function calculateFullBuildCost(characterName: string): Promise<{
    levelCost: BuildCost | null;
    talentCosts: {
        normal: TalentCost | null;
        skill: TalentCost | null;
        burst: TalentCost | null;
    };
    totalMora: number;
} | null> {
    try {
        const levelCost = await calculateBuildCost(characterName, 1, 90);
        const normalTalent = await calculateTalentCost(characterName, 'normal', 1, 9);
        const skillTalent = await calculateTalentCost(characterName, 'skill', 1, 9);
        const burstTalent = await calculateTalentCost(characterName, 'burst', 1, 9);
        
        const totalMora = 
            (levelCost?.mora || 0) + 
            (normalTalent?.mora || 0) + 
            (skillTalent?.mora || 0) + 
            (burstTalent?.mora || 0);
        
        return {
            levelCost,
            talentCosts: {
                normal: normalTalent,
                skill: skillTalent,
                burst: burstTalent
            },
            totalMora
        };
        
    } catch (error) {
        console.error('完全育成コスト計算エラー:', error);
        return null;
    }
} 