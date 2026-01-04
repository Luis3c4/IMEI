-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE public.product_items (
  id integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  variant_id integer NOT NULL,
  serial_number text NOT NULL UNIQUE,
  status text NOT NULL DEFAULT 'available'::text,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT product_items_pkey PRIMARY KEY (id),
  CONSTRAINT fk_variant FOREIGN KEY (variant_id) REFERENCES public.product_variants(id)
);
CREATE TABLE public.product_variants (
  id integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  product_id integer NOT NULL,
  color text NOT NULL,
  capacity text NOT NULL,
  price numeric NOT NULL CHECK (price >= 0::numeric),
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT product_variants_pkey PRIMARY KEY (id),
  CONSTRAINT fk_product FOREIGN KEY (product_id) REFERENCES public.products(id)
);
CREATE TABLE public.products (
  id integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  name text NOT NULL,
  category text,
  description text,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT products_pkey PRIMARY KEY (id)
);