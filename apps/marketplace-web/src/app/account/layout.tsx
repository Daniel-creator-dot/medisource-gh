import { AccountFrame } from "@/components/account-frame";
import type { ReactNode } from "react";

export default function AccountLayout({ children }: { children: ReactNode }) {
  return <AccountFrame>{children}</AccountFrame>;
}
