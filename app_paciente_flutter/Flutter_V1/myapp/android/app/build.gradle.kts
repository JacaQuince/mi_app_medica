// android/app/build.gradle.kts

plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")   // Kotlin Android plugin
    id("dev.flutter.flutter-gradle-plugin")
    id("com.google.gms.google-services")
}

android {
    namespace = "com.example.myapp"
    compileSdk = 35  // Cambia al SDK que estés usando

    ndkVersion = "27.0.12077973"

    defaultConfig {
        applicationId = "com.example.myapp"
        minSdk = 21
        targetSdk = 35
        versionCode = 1
        versionName = "1.0"
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            // shrinkResources no está disponible en Kotlin DSL directamente,
            // si quieres usarlo, deberás hacerlo en build.gradle (Groovy) o quitarlo
            // Por ahora, comentar o eliminar la siguiente línea:
            // shrinkResources = true 

            signingConfig = signingConfigs.getByName("debug")
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
        isCoreLibraryDesugaringEnabled = true
    }

    kotlinOptions {
        jvmTarget = "11"
    }
}

dependencies {
    implementation(platform("com.google.firebase:firebase-bom:33.14.0"))
    coreLibraryDesugaring("com.android.tools:desugar_jdk_libs:2.0.4")
    implementation("com.google.firebase:firebase-analytics")
}

flutter {
    source = "../.."
}
