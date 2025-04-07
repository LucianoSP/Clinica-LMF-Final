export interface StandardResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> extends StandardResponse<T[]> {
  items: T[];
  total: number;
  page: number;
  total_pages: number;
  has_more: boolean;
} 