import { Switch, Route } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { ThemeProvider } from "@/hooks/use-theme";
import { Header } from "@/components/Header";
import { BottomNav } from "@/components/BottomNav";
import UploadPage from "@/pages/UploadPage";
import SplitPage from "@/pages/SplitPage";
import MergePage from "@/pages/MergePage";
import StatsPage from "@/pages/StatsPage";
import NotFound from "@/pages/not-found";

function Router() {
  return (
    <Switch>
      <Route path="/" component={UploadPage} />
      <Route path="/split" component={SplitPage} />
      <Route path="/merge" component={MergePage} />
      <Route path="/stats" component={StatsPage} />
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <TooltipProvider>
          <div className="min-h-screen flex flex-col bg-background">
            <Header />
            <main className="flex-1 pb-20">
              <Router />
            </main>
            <BottomNav />
          </div>
          <Toaster />
        </TooltipProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
