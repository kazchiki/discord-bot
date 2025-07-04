export interface CharacterNames {
    [key: string]: string;
}

export interface PlayerInfo {
    nickname: string;
    level: number;
    worldLevel: number;
    towerFloorIndex: number;
    towerLevelIndex: number;
    signature?: string;
    profilePicture?: {
        avatarId: string;
    };
}

export interface PropMap {
    [key: string]: {
        val: number;
    };
}

export interface FightPropMap {
    [key: string]: number;
}

export interface ReliquaryMainstat {
    mainPropId: string;
    statValue: number;
}

export interface Flat {
    reliquaryMainstat?: ReliquaryMainstat;
    setNameTextMapHash?: string;
    equipType?: string;
}

export interface Reliquary {
    level: number;
}

export interface EquipItem {
    flat?: Flat;
    reliquary?: Reliquary;
}

export interface Character {
    avatarId: string;
    propMap: PropMap;
    fightPropMap?: FightPropMap;
    skillLevelMap?: { [key: string]: number };
    equipList?: EquipItem[];
}

export interface EnkaApiResponse {
    playerInfo?: PlayerInfo;
    avatarInfoList?: Character[];
} 