"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/taxonomy", label: "Taxonomy", icon: "\u{1F333}" },
  { href: "/classify", label: "Classify", icon: "\u{1F50D}" },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 border-r bg-muted/40 p-4 flex flex-col gap-2">
      <div className="mb-6">
        <h1 className="text-lg font-semibold">The Sorting Hat</h1>
        <p className="text-sm text-muted-foreground">IT Product Taxonomy</p>
      </div>
      <nav className="flex flex-col gap-1">
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              "flex items-center gap-2 rounded-md px-3 py-2 text-sm transition-colors",
              pathname.startsWith(item.href)
                ? "bg-primary text-primary-foreground"
                : "hover:bg-muted"
            )}
          >
            <span>{item.icon}</span>
            {item.label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
