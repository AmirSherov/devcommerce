import SimpleAuthForm from "@/components/ui/simple-auth-form";
import { GitHubBackground } from "@/components/ui/github-background";
import { Starfield } from "@/components/ui/starfield";
import ProtectedRoute from "@/components/ProtectedRoute";

export default function AuthPage() {
  return (
    <ProtectedRoute requireAuth={false}>
      <div className="min-h-screen bg-black relative overflow-hidden">
        <GitHubBackground />
        <div className="relative z-20">
          <SimpleAuthForm />
        </div>
      </div>
    </ProtectedRoute>
  );
} 