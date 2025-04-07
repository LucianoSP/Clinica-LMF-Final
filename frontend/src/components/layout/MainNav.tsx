import { LayoutDashboard, Users, FileText, BookOpen } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

interface NavItem {
  title: string;
  href?: string;
  icon?: any;
  items?: NavItem[];
}

const menuItems: NavItem[] = [
  {
    title: "Dashboard",
    href: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    title: "Cadastros",
    items: [
      {
        title: "Pacientes",
        href: "/cadastros/pacientes",
        icon: Users,
      },
      // Remova ou comente a opção de guias até estar pronta
      // {
      //   title: "Guias",
      //   href: "/cadastros/guias",
      //   icon: FileText,
      // },
    ],
  },
  {
    title: "Documentação",
    href: "/documentacao",
    icon: BookOpen,
  },
];

export function MainNav() {
  const pathname = usePathname();

  return (
    <nav className="space-y-1">
      {menuItems.map((item, index) => {
        // Se o item tem subitens, renderiza um grupo
        if (item.items) {
          return (
            <div key={index} className="space-y-1">
              <h2 className="px-3 text-sm font-medium text-gray-500">
                {item.title}
              </h2>
              <div className="space-y-1">
                {item.items.map((subItem, subIndex) => (
                  <Link
                    key={subIndex}
                    href={subItem.href || '#'}
                    className={cn(
                      "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium hover:bg-accent hover:text-accent-foreground",
                      pathname === subItem.href ? "bg-accent" : "transparent"
                    )}
                  >
                    {subItem.icon && <subItem.icon className="h-4 w-4" />}
                    {subItem.title}
                  </Link>
                ))}
              </div>
            </div>
          );
        }

        // Se não tem subitens, renderiza um link simples
        return (
          <Link
            key={index}
            href={item.href || '#'}
            className={cn(
              "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium hover:bg-accent hover:text-accent-foreground",
              pathname === item.href ? "bg-accent" : "transparent"
            )}
          >
            {item.icon && <item.icon className="h-4 w-4" />}
            {item.title}
          </Link>
        );
      })}
    </nav>
  );
} 