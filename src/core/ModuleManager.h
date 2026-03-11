#pragma once

#include "IModule.h"

#include <memory>
#include <vector>

class ModuleManager {
public:
    void registerModule(std::unique_ptr<IModule> module) {
        module->initialize();
        m_modules.push_back(std::move(module));
    }

    const std::vector<std::unique_ptr<IModule>>& modules() const {
        return m_modules;
    }

private:
    std::vector<std::unique_ptr<IModule>> m_modules;
};
