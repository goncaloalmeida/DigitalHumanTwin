#include "app/MainWindow.h"
#include "core/ModuleManager.h"
#include "modules/BodyProfileModule.h"

#include <QApplication>
#include <memory>

int main(int argc, char* argv[]) {
    QApplication app(argc, argv);

    ModuleManager moduleManager;
    moduleManager.registerModule(std::make_unique<BodyProfileModule>());

    MainWindow window;
    window.setModuleManager(&moduleManager);
    window.show();

    return app.exec();
}
