"use client";

import { apiRequest } from "@medisource/api-client";
import { Button, Card } from "@medisource/ui";
import type { Envelope, NotificationItem } from "@medisource/shared-types";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { EmptyState } from "@/components/states";

export default function NotificationsPage() {
  const queryClient = useQueryClient();
  const notes = useQuery({
    queryKey: ["notifications"],
    queryFn: () => apiRequest<Envelope<NotificationItem[]>>("/api/v1/account/notifications/"),
  });
  const markRead = useMutation({
    mutationFn: async (id: string) => {
      const csrf = await apiRequest<Envelope<{ csrf_token: string }>>("/api/v1/auth/csrf/");
      return apiRequest(`/api/v1/account/notifications/${id}/`, {
        method: "PATCH",
        body: {},
        csrfToken: csrf.data.csrf_token,
      });
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["notifications"] });
    },
  });
  const rows = notes.data?.data ?? [];
  return (
    <div>
      <h1 className="text-3xl font-semibold text-navy">Notifications</h1>
      <p className="mt-2 text-sm text-muted">These are account notices stored for you. Other customers cannot read them.</p>
      {rows.length === 0 ? (
        <div className="mt-6">
          <EmptyState title="No notifications" body="A welcome notice is created when you register. Older demo accounts may have none." />
        </div>
      ) : (
        <div className="mt-6 grid gap-3">
          {rows.map((note) => (
            <Card key={note.id} className="p-4">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="font-semibold text-navy">{note.title}</p>
                  <p className="mt-1 text-sm leading-6 text-muted">{note.body}</p>
                </div>
                {note.is_read ? (
                  <span className="text-xs font-semibold text-success">Read</span>
                ) : (
                  <Button size="sm" variant="secondary" onClick={() => markRead.mutate(note.id)}>
                    Mark read
                  </Button>
                )}
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
