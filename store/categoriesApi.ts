import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

export type Category = {
  id: number;
  name: string;
  imageUrl: string;
};

export type CreateCategoryPayload = {
  name: string;
  imageUrl: string;
};

const API_BASE_URL =
  process.env.EXPO_PUBLIC_API_URL ??
  'http://192.168.88.102:5007/api';

export const categoriesApi = createApi({
  reducerPath: 'categoriesApi',
  tagTypes: ['Categories'],

  baseQuery: fetchBaseQuery({
    baseUrl: API_BASE_URL,
  }),

  endpoints: (builder) => ({
    getCategories: builder.query<Category[], void>({
      query: () => '/categories',

      providesTags: (result) =>
        result
          ? [
              ...result.map(({ id }) => ({
                type: 'Categories' as const,
                id,
              })),
              { type: 'Categories', id: 'LIST' },
            ]
          : [{ type: 'Categories', id: 'LIST' }],
    }),

    createCategory: builder.mutation<Category, CreateCategoryPayload>({
      query: (body) => ({
        url: '/categories',
        method: 'POST',
        body,
      }),

      invalidatesTags: [{ type: 'Categories', id: 'LIST' }],
    }),

    deleteCategory: builder.mutation<void, number>({
      query: (id) => ({
        url: `/categories/${id}`,
        method: 'DELETE',
      }),

      invalidatesTags: (result, error, id) => [
        { type: 'Categories', id },
        { type: 'Categories', id: 'LIST' },
      ],
    }),
  }),
});

export const {
  useGetCategoriesQuery,
  useCreateCategoryMutation,
  useDeleteCategoryMutation,
} = categoriesApi;