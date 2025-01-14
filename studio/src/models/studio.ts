import { Static } from "vue";

export interface Connection<T> {
  pageInfo: PageInfo;
  edges: Edge<T>[];
  totalCount: number;
}

export interface Edge<T> {
  cursor: string;
  node: T;
}

export interface StudioGraph {
  mediaTypes: MediaType[];
  users: User[];
  stages: Stage[];
  tags: Tag[];
  media: Connection<Media>;
  whoami: User;
  notifications: Notification[];
  voices: VoiceGraph[];
  adminPlayers: Connection<User>;
}

export interface VoiceGraph {
  avatar: Media;
  voice: AvatarVoice;
}

export interface PageInfo {
  startCursor: string;
  endCursor: string;
  hasNextPage: boolean;
  hasPreviousPage: boolean;
}

export interface MediaType {
  id: string;
  name: string;
}

export interface User {
  id: string;
  active: boolean;
  username: string;
  email: string;
  binName: string;
  role: number;
  roleName: string;
  firstName: string;
  lastName: string;
  displayName: string;
  createdOn: string;
  uploadLimit: number;
  intro: string | null;
  dbId: number;
}

export interface Stage {
  id: string;
  name: string;
  dbId: number;
  createdOn: Date;
  owner: User;
  fileLocation: string;
  visibility: boolean;
  status: "live" | "rehearsal" | "upcoming";
}

export interface Tag {
  id: string;
  name: string;
  dbId: number;
}

export interface AssignedStage {
  id: number;
  name: string;
  url: string;
}

export type CopyrightLevel = 0 | 1 | 2 | 3;

export const uploadDefault = 1024 * 1024;

export interface Media {
  id: string;
  name: string;
  fileLocation: string;
  sign: string;
  description: string;
  createdOn: string;
  size: number;
  copyrightLevel: CopyrightLevel;
  permissions: Permission[];
  assetType: MediaType;
  owner: User;
  stages: AssignedStage[];
  tags: string[];
  privilege: Privilege;
}

export interface MediaAttributes {
  multi: boolean;
  frames: string[];
  voice: AvatarVoice;
  link: Link;
  w: number;
  h: number;
  note: string;
}

export interface Link {
  blank: boolean;
  effect: boolean;
  url: string;
}

export interface UploadFile {
  action?: string;
  filename?: string;
  data?: any;
  file: File;
  headers?: any;
  withCredentials?: boolean;
  method?: string;
  id: number;
  preview: string;
  status: "local" | "uploaded" | "virtual";
  url?: string;
}

export interface Permission {
  id: string;
  approved: boolean;
  userId: number;
  assetId: number;
  seen: boolean;
  createdOn: string;
  note: null;
  user: User;
  asset: Media;
}

export interface Notification {
  id: string;
  type: "MEDIA_USAGE";
  mediaUsage: Permission;
}

export interface AvatarVoice {
  voice: string;
  variant: string;
  pitch: number;
  speed: number;
  amplitude: number;
}

export type Privilege =
  | "NONE"
  | "OWNER"
  | "APPROVED"
  | "PENDING_APPROVAL"
  | "REQUIRE_APPROVAL";
