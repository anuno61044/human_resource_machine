// utils/types.ts

export interface Agent {
    id: number;
    name: string;
    memory: number;
    pythonCode: string;
    _type: boolean;
    function: number[];
}

export interface Functionality {
    id: number;
    name: string;
}
