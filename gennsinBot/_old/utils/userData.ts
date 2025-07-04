import fs from 'fs/promises';
import path from 'path';
import { Character } from '../types';

// ユーザーデータの型定義
interface SavedCharacter {
    data: Character;
    characterName: string;
    lastUpdated: string;
}

export interface AccountData {
    nickname?: string;
    lastUpdated: string;
    characters?: {
        [characterId: string]: SavedCharacter;
    };
}

interface UserData {
    [discordUserId: string]: {
        currentUID: string;  // 現在アクティブなUID
        accounts: {
            [uid: string]: AccountData;
        };
    };
}

const USER_DATA_FILE = path.join(process.cwd(), 'userData.json');

// ユーザーデータを読み込み
export async function loadUserData(): Promise<UserData> {
    try {
        const data = await fs.readFile(USER_DATA_FILE, 'utf-8');
        return JSON.parse(data);
    } catch (error) {
        // ファイルが存在しない場合は空オブジェクトを返す
        return {};
    }
}

// ユーザーデータを保存
export async function saveUserData(userData: UserData): Promise<void> {
    try {
        await fs.writeFile(USER_DATA_FILE, JSON.stringify(userData, null, 2), 'utf-8');
    } catch (error) {
        console.error('ユーザーデータの保存に失敗しました:', error);
        throw error;
    }
}

// ユーザーの現在のUIDを取得
export async function getUserUID(discordUserId: string): Promise<string | null> {
    const userData = await loadUserData();
    return userData[discordUserId]?.currentUID || null;
}

// ユーザーのUIDを登録/更新
export async function setUserUID(discordUserId: string, uid: string, nickname?: string): Promise<void> {
    const userData = await loadUserData();
    
    if (!userData[discordUserId]) {
        userData[discordUserId] = {
            currentUID: uid,
            accounts: {}
        };
    } else {
        userData[discordUserId].currentUID = uid;
    }
    
    // アカウント情報を登録/更新
    userData[discordUserId].accounts[uid] = {
        nickname,
        lastUpdated: new Date().toISOString(),
        characters: userData[discordUserId].accounts[uid]?.characters || {}
    };
    
    await saveUserData(userData);
}

// ユーザーのデータを削除
export async function deleteUserData(discordUserId: string): Promise<boolean> {
    const userData = await loadUserData();
    
    if (userData[discordUserId]) {
        delete userData[discordUserId];
        await saveUserData(userData);
        return true;
    }
    
    return false;
}

// ユーザーのキャラクター情報を保存
export async function saveUserCharacter(
    discordUserId: string, 
    uid: string,
    characterId: string, 
    characterData: Character, 
    characterName: string
): Promise<void> {
    const userData = await loadUserData();
    
    if (!userData[discordUserId]) {
        throw new Error('ユーザーが登録されていません');
    }
    
    if (!userData[discordUserId].accounts[uid]) {
        throw new Error('指定されたUIDが登録されていません');
    }
    
    if (!userData[discordUserId].accounts[uid].characters) {
        userData[discordUserId].accounts[uid].characters = {};
    }
    
    userData[discordUserId].accounts[uid].characters![characterId] = {
        data: characterData,
        characterName,
        lastUpdated: new Date().toISOString()
    };
    
    await saveUserData(userData);
}

// ユーザーの保存されたキャラクター一覧を取得（現在のUIDのもの）
export async function getUserCharacters(discordUserId: string): Promise<{ [characterId: string]: SavedCharacter } | null> {
    const userData = await loadUserData();
    const currentUID = userData[discordUserId]?.currentUID;
    if (!currentUID) return null;
    
    return userData[discordUserId]?.accounts[currentUID]?.characters || null;
}

// 特定UIDのキャラクター一覧を取得
export async function getUserCharactersByUID(discordUserId: string, uid: string): Promise<{ [characterId: string]: SavedCharacter } | null> {
    const userData = await loadUserData();
    return userData[discordUserId]?.accounts[uid]?.characters || null;
}

// ユーザーの特定キャラクター情報を取得（現在のUIDのもの）
export async function getUserCharacter(discordUserId: string, characterId: string): Promise<SavedCharacter | null> {
    const userData = await loadUserData();
    const currentUID = userData[discordUserId]?.currentUID;
    if (!currentUID) return null;
    
    return userData[discordUserId]?.accounts[currentUID]?.characters?.[characterId] || null;
}

// ユーザーの特定キャラクター情報を削除（現在のUIDのもの）
export async function deleteUserCharacter(discordUserId: string, characterId: string): Promise<boolean> {
    const userData = await loadUserData();
    const currentUID = userData[discordUserId]?.currentUID;
    if (!currentUID) return false;
    
    if (userData[discordUserId]?.accounts[currentUID]?.characters?.[characterId]) {
        delete userData[discordUserId].accounts[currentUID].characters![characterId];
        await saveUserData(userData);
        return true;
    }
    
    return false;
}

// ユーザーのアカウント一覧を取得
export async function getUserAccounts(discordUserId: string): Promise<{ [uid: string]: AccountData } | null> {
    const userData = await loadUserData();
    return userData[discordUserId]?.accounts || null;
}

// アクティブUIDを切り替え
export async function switchActiveUID(discordUserId: string, uid: string): Promise<boolean> {
    const userData = await loadUserData();
    
    if (!userData[discordUserId]?.accounts[uid]) {
        return false; // 指定されたUIDが存在しない
    }
    
    userData[discordUserId].currentUID = uid;
    await saveUserData(userData);
    return true;
} 