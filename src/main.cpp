#include "app/MainWindow.h"
#include "core/ModuleManager.h"

#include <QApplication>

int main(int argc, char* argv[]) {
    QApplication app(argc, argv);

    ModuleManager moduleManager;

    MainWindow window;
    window.setModuleManager(&moduleManager);
    window.show();

    return app.exec();
}
