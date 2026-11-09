package org.telegram.ui;

import android.content.ComponentName;
import android.content.Context;
import android.content.pm.PackageManager;

import org.telegram.messenger.ApplicationLoader;
import org.telegram.messenger.R;

public class LauncherIconController {
    public static void tryFixLauncherIconIfNeeded() {
        for (LauncherIcon icon : LauncherIcon.values()) {
            if (isEnabled(icon)) {
                return;
            }
        }

        setIcon(LauncherIcon.BLUE);
    }

    public static boolean isEnabled(LauncherIcon icon) {
        Context ctx = ApplicationLoader.applicationContext;
        int i = ctx.getPackageManager().getComponentEnabledSetting(icon.getComponentName(ctx));
        return i == PackageManager.COMPONENT_ENABLED_STATE_ENABLED || i == PackageManager.COMPONENT_ENABLED_STATE_DEFAULT && icon == LauncherIcon.BLUE;
    }

    public static void setIcon(LauncherIcon icon) {
        Context ctx = ApplicationLoader.applicationContext;
        PackageManager pm = ctx.getPackageManager();
        for (LauncherIcon i : LauncherIcon.values()) {
            pm.setComponentEnabledSetting(i.getComponentName(ctx), i == icon ? PackageManager.COMPONENT_ENABLED_STATE_ENABLED :
                    PackageManager.COMPONENT_ENABLED_STATE_DISABLED, PackageManager.DONT_KILL_APP);
        }
    }

    public enum LauncherIcon {
        DEFAULT("DefaultIcon", R.drawable.msngram_default_background, R.drawable.msngram_default_foreground, R.string.AppIconDefault),
        GOOGLE("GoogleIcon", R.drawable.msngram_google_background, R.drawable.msngram_google_foreground, R.string.AppIconGoogle),
        COLORFUL("ColorfulIcon", R.drawable.msngram_colorful_background, R.drawable.msngram_colorful_foreground, R.string.AppIconColorful),
        DARKGREEN("DarkGreenIcon", R.drawable.msngram_darkgreen_background, R.drawable.msngram_darkgreen_foreground, R.string.AppIconDarkGreen),
        NEON("NeonIcon", R.drawable.msngram_neon_background, R.drawable.msngram_neon_foreground, R.string.AppIconNeon),
        NIELLO("NielloIcon", R.drawable.msngram_niello_background, R.drawable.msngram_niello_foreground, R.string.AppIconNiello),
        BLUE("BlueIcon", R.drawable.msngram_blue_background, R.drawable.msngram_blue_foreground, R.string.AppIconBlue),
        DARKBLUE("DarkBlueIcon", R.drawable.msngram_darkblue_background, R.drawable.msngram_darkblue_foreground, R.string.AppIconDarkBlue),
        BLURBLUE("BlurBlueIcon", R.drawable.msngram_blurblue_background, R.drawable.msngram_blurblue_foreground, R.string.AppIconBlurBlue),
        TELEGRAM("TelegramIcon", R.drawable.msngram_telegram_background, R.drawable.msngram_telegram_foreground, R.string.AppIconTelegramOriginal),
        VINTAGE("VintageIcon", R.drawable.msngram_vintage_background, R.drawable.msngram_vintage_foreground, R.string.AppIconVintage),
        AQUA("AquaIcon", R.drawable.msngram_aqua_background, R.drawable.msngram_aqua_foreground, R.string.AppIconAqua),
        PREMIUM("PremiumIcon", R.drawable.msngram_premium_background, R.drawable.msngram_premium_foreground, R.string.AppIconPremium),
        TURBO("TurboIcon", R.drawable.msngram_turbo_background, R.drawable.msngram_turbo_foreground, R.string.AppIconTurbo),
        NOX("NoxIcon", R.drawable.msngram_nox_background, R.drawable.msngram_nox_foreground, R.string.AppIconNox);

        public final String key;
        public final int background;
        public final int foreground;
        public final int title;
        public final boolean premium;

        private ComponentName componentName;

        public ComponentName getComponentName(Context ctx) {
            if (componentName == null) {
                componentName = new ComponentName(ctx.getPackageName(), "org.telegram.messenger." + key);
            }
            return componentName;
        }

        LauncherIcon(String key, int background, int foreground, int title) {
            this(key, background, foreground, title, false);
        }

        LauncherIcon(String key, int background, int foreground, int title, boolean premium) {
            this.key = key;
            this.background = background;
            this.foreground = foreground;
            this.title = title;
            this.premium = premium;
        }

        public boolean isNekoX() {
            // Every MSNgram choice uses an adaptive background and folded-M layer.
            return false;
        }
    }
}
