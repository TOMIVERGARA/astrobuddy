import { type VariantProps, tv } from "tailwind-variants";
import Root from "./toggle.svelte";

export const toggleVariants = tv({
	base: "inline-flex items-center justify-center rounded-none text-sm font-medium transition-all focus-visible:outline-none disabled:pointer-events-none disabled:opacity-50 data-[state=on]:bg-white data-[state=on]:text-black uppercase tracking-wider",
	variants: {
		variant: {
			default: "bg-transparent hover:bg-neutral-600/20 text-neutral-500 data-[state=on]:text-black",
			outline: "border border-neutral-700 bg-transparent hover:bg-neutral-600/20 text-neutral-500 data-[state=on]:border-white",
		},
		size: {
			default: "h-10 px-3",
			sm: "h-9 px-2.5",
			lg: "h-11 px-5",
		},
	},
	defaultVariants: {
		variant: "default",
		size: "default",
	},
});

export type Variant = VariantProps<typeof toggleVariants>["variant"];
export type Size = VariantProps<typeof toggleVariants>["size"];

export {
	Root,
	//
	Root as Toggle,
};
